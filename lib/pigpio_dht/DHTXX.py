import pigpio
from time import time, sleep
from datetime import datetime
import statistics

DEBUG = False

"""
DHT Sensor Base Constructor
"""
class DHTXX:

    SUCCESS_EDGE_COUNT = 86 # Expected number of edges for a successful sensor communication.
    EXPECTED_DATA_BITS = 40 # Expected number of data bytes to be returned from the sensor.

    def __init__(self, gpio, timeout_secs=0.5, use_internal_pullup=True, pi=None, max_read_rate_secs=2, datum_byte_count=1):
        """
        Base Constructor.

        :param gpio: BCM Pin of sensor
        :type gpio: Integer
        :param timeout_secs: sensor read timeout in seconds
        :type timeout_secs: integer
        :param use_internal_pullup: enable internal pull-up resistor on gpio
        :type use_internal_pullup: boolean
        :param pi: Custom instance of pigpio.pi()
        :type pi: pigpio
        :param max_read_rate_secs: time in seconds between allowed sensor reads.
        :type max_read_rate_secs: integer
        :param datum_byte_count: number of bytes used to represent temperature and humidity data for sensor
        :type datum_byte_count: integer in range 1..2
        """
        assert(datum_byte_count in (1,2))

        self.gpio = gpio
        self.timeout_secs = timeout_secs
        self.read_success = False
        self.sensor_responded = False
        self.data = []

        if pi != None:
            self.__pi = pi
        else:
            self.__pi = pigpio.pi()

        if use_internal_pullup:
            self.__pi.set_pull_up_down(gpio, pigpio.PUD_UP)

        self.__datum_byte_count = datum_byte_count
        self.__max_read_rate_secs = max_read_rate_secs
        self.__bit_count = -1
        self.__last_tick = -1
        self.__edge_count = -1
        self.__last_read_time = None

        self.__c0 = -1 # timing variables for debugging and testing.
        self.__c1 = -1


    def read(self, retries=0):
        """
        One-shot sensor read.
        read() will add in a pause if you try and call it more than once per max_read_rate_secs.

        :param retries: number of times to retry when checksum validation fails
        :type retries: integer
        :return: Sensor data like {'temp_c': 20, 'temp_f': 68.0, 'humidity': 35, 'valid': True}
        :rtype: Dictionary
        :raises TimeoutError: If the sensor on gpio does not respond
        """
        retries = abs(retries) + 1

        for i in range(retries):
            result = self.__read()

            if result['valid'] == True:
                break

        return result


    def sample(self, samples=5, max_retries=None):
        """
        Sample sensor and return normalised data.

        :param samples: number of samples to take
        :type samples: integer
        :param max_retries: maximum retries per sample before raising exception. Default 2 * samples
        :type max_retries: integer
        :return: Sensor data like {'temp_c': 20, 'temp_f': 68.0, 'humidity': 35, 'valid': True}
        :rtype: Dictionary
        :raises TimeoutError: If the sensor on gpio does not respond, or max_retries is reached
        """
        samples = max(2, samples)

        if max_retries is None:
            max_retries = samples * 2

        sample_num = 0
        trim_sd = 1  # Number of standard deviations to trim.
        retries = 0
        temperatures = []
        humidities = []
        initial_result = None  # For debugging and testing results.

        while len(temperatures) < samples:
            sample_num += 1
            _debug("--- SAMPLE {} ----".format(sample_num)) 
            result = self.read(retries=0)

            if (len(temperatures) == 0):
                # Capture initial result
                initial_result = result
            
            if result['valid']:
                temperatures.append(result['temp_c'])
                humidities.append(result['humidity'])
            else:
                retries += 1

            if retries >= max_retries:
                raise TimeoutError("Maximum retries of {} reached.".format(max_retries))

        _debug("Retries:", retries)

        # Temperature
        temp_sd = statistics.stdev(temperatures)
        temp_mean = statistics.mean(temperatures)
        if temp_sd == 0:
            temperatures_norm = temperatures
        else:
            temperatures_norm = [x for x in temperatures if (x > temp_mean - trim_sd * temp_sd)]
            temperatures_norm = [x for x in temperatures_norm if (x < temp_mean + trim_sd * temp_sd)]

        _debug("temps, norm", temperatures, temperatures_norm)

        temp_mean = statistics.mean(temperatures_norm)
        temp_mode = None
        try:
            temp_mode = statistics.mode(temperatures_norm)
        except:
            pass # no mode.        
        
        _debug("temps, sd, mean, mode =", temperatures, temperatures_norm, temp_sd, temp_mean, temp_mode)
        temp_c = temp_mode if temp_mode else temp_mean
        temp_c = round(temp_c, 1)

        # Humidity
        humidity_sd = statistics.stdev(humidities)
        humidity_mean = statistics.mean(humidities)
        if humidity_sd == 0:
            humidities_norm = humidities
        else:
            humidities_norm = [x for x in humidities if (x > humidity_mean - trim_sd * humidity_sd)]
            humidities_norm = [x for x in humidities_norm if (x < humidity_mean + trim_sd * humidity_sd)]

        _debug("humidities, norm", humidities, humidities_norm)

        humidity_mean = statistics.mean(humidities_norm)
        humidity_mode = None
        try:
            humidity_mode = statistics.mode(humidities_norm)
        except:
            pass # no mode.

        _debug("humidities, sd, mean, mode =", humidities, humidities_norm, humidity_sd, humidity_mean, humidity_mode)
        humidity = humidity_mode if humidity_mode else humidity_mean
        humidity = round(humidity, 1)

        temp_f = (temp_c * 9/5) + 32
        temp_f = round(temp_f, 1)
        valid = True # Else would have thrown exception above.

        if DEBUG:
            temp_fixed = initial_result['temp_c'] != temp_c
            humidity_fixed = initial_result['humidity'] != humidity

            result = {
                'init_temp_c': initial_result['temp_c'],
                'init_temp_f': initial_result['temp_f'],
                'init_humidity': initial_result['humidity'],
                'temp_c': temp_c,
                'temp_f': temp_f,
                'temp_fixed': temp_fixed,
                'humidity': humidity,
                'humidity_fixed': humidity_fixed,
                'samples': samples,
                'valid': valid,
                'temp_sd': temp_sd,
                'temp_mean': temp_mean,
                'temp_mode': temp_mode,
                'humidity_sd': humidity_sd,
                'humidity_mean': humidity_mean,
                'humidity_mode': humidity_mode}            
        else:
            result = {
                'temp_c': temp_c,
                'temp_f': temp_f,
                'humidity': humidity,
                'valid': valid}

        return result


    def __read(self):
        """
        One-Shot read implementation.
        __read() monitors the read rate self.__max)read_rate_secs and will pause between successive calls.
        :return: Sensor data like {'temp_c': 20, 'temp_f': 68.0, 'humidity': 35, 'valid': True}
        :rtype: Dictionary
        """

        # Throttle reads so we are not reading more than once per self.__max_read_rate_secs 
        if (self.__last_read_time): 
            elapsed_since_last_read = (datetime.now() - self.__last_read_time).microseconds / 1000000

            if (elapsed_since_last_read < self.__max_read_rate_secs):
                pause_secs = self.__max_read_rate_secs - elapsed_since_last_read
                _debug("Pausing for secs", pause_secs)
                sleep(pause_secs)
                    
        self.__edge_count = 0
        self.__bit_count = 0
        self.read_success = False
        self.sensor_responded = False
        self.data = []
        self.__last_tick = self.__pi.get_current_tick()
        self.__last_read_time = datetime.now()
        self.__c0 = self.__last_tick

        self.__edge_callback_fn = self.__pi.callback(self.gpio, pigpio.EITHER_EDGE, self.__edge_callback)

        self.__pi.set_mode(self.gpio, pigpio.OUTPUT)
        self.__pi.write(self.gpio, pigpio.LOW)
        sleep(0.018)  # 18ms pause as per datasheet
        #No! self.__pi.write(self.gpio, pigpio.HIGH)
        self.__pi.set_mode(self.gpio, pigpio.INPUT)

        # Sleep while __edge_callback is called.
        sleep(self.timeout_secs)
        self.__edge_callback_fn.cancel()

        if DEBUG:
            elapsed_secs = (self.__c1 - self.__c0) / 1000000
            _debug("Edge Count", self.__edge_count)
            _debug("Data Length", len(self.data))
            _debug("Round Trip Secs:", elapsed_secs)
            _debug("Sensor Response?", self.sensor_responded)
            _debug("Read Success?", self.read_success)

        if not self.sensor_responded:
            raise TimeoutError("{} sensor on GPIO {} has not responded in {} seconds. Check sensor connection.".format(self.__class__.__name__, self.gpio, self.timeout_secs))
        elif not self.read_success:
                # note: self.__edge_count == DHTXX.SUCCESS_EDGE_COUNT when self.read_success == True
                raise TimeoutError("{} sensor on GPIO {} responded but the response was invalid. Check sensor connection or try increasing timeout (currently {} seconds).".format(self.__class__.__name__, self.gpio, self.timeout_secs))

        return self._parse_data()


    def _parse_data(self):
        """
        Parse data data from sensor into temperature and humidity.
        :return: Sensor data like {'temp_c': 20, 'temp_f': 68.0, 'humidity': 35, 'valid': True}
        :rtype: Dictionary
        """

        bytes = []
        byte = 0

        for i in range(len(self.data)):
            bit = self.data[i]
            byte = (byte << 1) | bit
            if ((i + 1) % 8 == 0):
                bytes.append(byte)
                byte = 0

        assert(len(bytes) == 5)

        if DEBUG:
            _debug("len(data) =", len(self.data))
            _debug("data =", self.data)
            _debug("bytes =", bytes)

        humidity = 0
        temp_c = 0
        temp_f = 0

        valid = (bytes[0] + bytes[1] + bytes[2] + bytes[3]) & 255 == bytes[4]

        if self.__datum_byte_count == 1:
            # Data is single byte, eg DHT11
            temp_c = round(bytes[2])
            temp_f = round((temp_c * 9/5) + 32, 1)
            humidity = round(bytes[0], 1)

        else:
            # Data is 2 bytes, eg DHT22
            multiplier = 1  # Positive or negative temp multiplier

            if bytes[2] & 0b10000000:
                multiplier = -1
                bytes[2] = bytes[2] ^ 0b10000000

            temp_c =  round(multiplier * float(bytes[2] * 256 + bytes[3]) / 10, 1)
            temp_f = round((temp_c * 9/5) + 32, 1)
            humidity = round(float(bytes[0] * 256 + bytes[1]) / 10, 1)

        if not valid:
            humidity = 0
            temp_c = 0
            temp_f = 0

        return {'temp_c': temp_c,
                'temp_f': temp_f,
                'humidity': humidity,
                'valid': valid}


    def __edge_callback(self, gpio, level, tick):
        """
        pigpio callback handler that monitors GPIO pin and collects sensor response.
        """

        hl_text = "HIGH" if level == 1 else "LOW" # For debugging output.

        if self.__edge_count <= 1:
          _debug(self.__edge_count, "RPI->DHT", "Request Data", hl_text)

        elif self.__edge_count <= 3:
          self.sensor_responded = True
          _debug(self.__edge_count, "RPI<-DHT", "Transmission Starting", hl_text)

        elif self.__edge_count <= 4:
          # Initial data stream LOW
          _debug(self.__edge_count, "RPI<-DHT", "Data (Initial LOW)", hl_text)

        elif self.__edge_count <= 84:
          _debug(self.__edge_count, "RPI<-DHT", "Data", hl_text)

          elapsed = tick - self.__last_tick
          self.__last_tick = tick

          if level == 0:
              bit = 1 if elapsed >= 70 else 0
              self.data.append(bit)
              _debug("  Elapsed microseconds={}, so data[{}]={}".format(elapsed, self.__bit_count, bit));
              self.__bit_count += 1
              
        else:
          _debug(self.__edge_count, "RPI<-DHT", "Data (Transmiation Complete)", hl_text)
          self.__edge_callback_fn.cancel()
          self.read_success = len(self.data) == DHTXX.EXPECTED_DATA_BITS
          self.__c1 = self.__pi.get_current_tick()
          assert(level == pigpio.HIGH)  # GPIO is high when transmission is complete (sensor 'free' state per datasheet)
          assert(self.__edge_count == DHTXX.SUCCESS_EDGE_COUNT-1) # -1 because __edge_count += 1 below.
          
        self.__last_tick = tick
        self.__edge_count += 1


def _debug(*texts):
    if not DEBUG:
        return
    print(' '.join(str(t) for t in texts))

