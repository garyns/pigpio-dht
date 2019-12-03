import pigpio
from time import time, sleep
from datetime import datetime
import statistics

class DHTXX:

    DEBUG = False
    SUCCESS_EDGE_COUNT = 86
    EXPECTED_DATA_BITS = 40

    def __init__(self, gpio, pi=None, timeout_secs=0.5, max_read_rate_secs=2, datum_byte_count=1):
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

        self.__pi.set_pull_up_down(gpio, pigpio.PUD_UP)

        self.__datum_byte_count = datum_byte_count
        self.__max_read_rate_secs = max_read_rate_secs
        self.__bit_count = -1
        self.__last_tick = -1
        self.__edge_count = -1
        self.__last_read_time = None

        self.__c0 = -1
        self.__c1 = -1


    def read(self, retries=0):
        retries = abs(retries) + 1

        for i in range(retries):
            result = self.__read()

            if result['valid'] == True:
                break

        return result


    def sample(self, samples=5, max_retries=None):
        samples = max(2, samples)

        if max_retries is None:
            max_retries = samples * 2

        trim_sd = 1  # Number of standard deviations to trim.
        retries = 0
        temperatures = []
        humidities = []
        initial_result = None

        while len(temperatures) < samples:
            result = self.read(retries=0)

            if (len(temperatures) == 0):
                initial_result = result
            
            if result['valid']:
                temperatures.append(result['temp_c'])
                humidities.append(result['humidity'])
            else:
                retries += 1

            if retries >= max_retries:
                raise TimeoutError("Maximum retries of {} reached.".format(max_retries))

        if DHTXX.DEBUG: print("Retries:", retries)

        # Temperature
        temp_sd = statistics.stdev(temperatures)
        temp_mean = statistics.mean(temperatures)
        if temp_sd == 0:
            temperatures_norm = temperatures
        else:
            temperatures_norm = [x for x in temperatures if (x > temp_mean - trim_sd * temp_sd)]
            temperatures_norm = [x for x in temperatures_norm if (x < temp_mean + trim_sd * temp_sd)]

        if DHTXX.DEBUG: print("temps, norm", temperatures, temperatures_norm)

        temp_mean = statistics.mean(temperatures_norm)
        temp_mode = None
        try:
            temp_mode = statistics.mode(temperatures_norm)
        except:
            pass # no mode.        
        
        if DHTXX.DEBUG: print("temps, sd, mean, mode =", temperatures, temperatures_norm, temp_sd, temp_mean, temp_mode)
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

        if DHTXX.DEBUG: print("humidities, norm", humidities, humidities_norm)

        humidity_mean = statistics.mean(humidities_norm)
        humidity_mode = None
        try:
            humidity_mode = statistics.mode(humidities_norm)
        except:
            pass # no mode.

        if DHTXX.DEBUG: print("humidities, sd, mean, mode =", humidities, humidities_norm, humidity_sd, humidity_mean, humidity_mode)
        humidity = humidity_mode if humidity_mode else humidity_mean
        humidity = round(humidity, 1)

        temp_f = (temp_c * 9/5) + 32
        temp_f = round(temp_f, 1)
        valid = True # Else would have thrown exception above.

        if DHTXX.DEBUG:

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
            result = {'temp_c': temp_c,
                'temp_f': temp_f,
                'humidity': humidity,
                'valid': valid}

        return result


    def __read(self):

        # Throttle reads so we are not reading more than once per self.__max_read_rate_secs 
#        elapsed_since_last_read = self.__pi.get_current_tick() - self.__last_read_time 
#         if (elapsed_since_last_read < (self.__max_read_rate_secs * 1000000)):
#             pause_secs = ((self.__max_read_rate_secs * 1000000) - elapsed_since_last_read) / 1000000
#             if DHTXX.DEBUG: print("Pausing for secs", pause_secs)
#             print("Pausing for secs", pause_secs)
#             sleep(pause_secs)
        # Throttle reads so we are not reading more than once per self.__max_read_rate_secs 
        if (self.__last_read_time): 
            elapsed_since_last_read = (datetime.now() - self.__last_read_time).microseconds / 1000000
            print(elapsed_since_last_read)
            if (elapsed_since_last_read < self.__max_read_rate_secs):
                pause_secs = self.__max_read_rate_secs - elapsed_since_last_read
                if DHTXX.DEBUG: print("Pausing for secs", pause_secs)
                print("Pausing for secs", pause_secs)
                sleep(pause_secs)
                    

        self.__edge_count = 0
        self.read_success = False
        self.sensor_responded = False
        self.data = []
        self.__last_tick = self.__pi.get_current_tick()
        self. __last_read_time = datetime.now()
        self.__c0 = self.__last_tick

        self.__edge_callback_fn = self.__pi.callback(self.gpio, pigpio.EITHER_EDGE, self.__edge_callback)

        self.__pi.set_mode(self.gpio, pigpio.OUTPUT)
        self.__pi.write(self.gpio, pigpio.LOW)
        sleep(0.018)  # 18ms pause as per datasheet
        self.__pi.write(self.gpio, pigpio.HIGH)

        self.__pi.set_mode(self.gpio, pigpio.INPUT)

        sleep(self.timeout_secs)
        self.__edge_callback_fn.cancel()

        if DHTXX.DEBUG:
            elapsed_secs = (self.__c1 - self.__c0) / 1000000
            print("Round Trip Secs:", elapsed_secs)
            print("Sensor Response?", self.sensor_responded)
            print("Read Success?", self.read_success)

        if not self.sensor_responded:
            raise TimeoutError("{} sensor on GPIO {} has not responded in {} seconds. Check sensor connection.".format(self.__class__.__name__, self.gpio, self.timeout_secs))
        elif not self.read_success:
                # note: self.__edge_count == DHTXX.SUCCESS_EDGE_COUNT when self.read_success == True
                raise TimeoutError("{} sensor on GPIO {} responded but the response invalid. Check sensor connection or try increasing timeout (currently {} seconds).".format(self.__class__.__name__, self.gpio, self.timeout_secs))

        return self.__parse_data()

    def __parse_data(self):

        bytes = []
        byte = 0

        for i in range(len(self.data)):
            bit = self.data[i]
            byte = (byte << 1) | bit
            if ((i + 1) % 8 == 0):
                bytes.append(byte)
                byte = 0

#        for i in range(0, len(self.data)):
#            byte = byte << 1
#            if (self.data[i]):
#             byte = byte | 1
#            else:
#              byte = byte | 0
#  
#            if ((i + 1) % 8 == 0):
#                bytes.append(byte)
#                byte = 0

        valid = (bytes[0] + bytes[1] + bytes[2] + bytes[3]) == bytes[4]

        if DHTXX.DEBUG:
            print("len(data) =", len(self.data))
            print("data =", self.data)
            print("bytes =", bytes)

        humidity = 0
        temp_c = 0
        temp_f = 0

        if valid:

            if self.__datum_byte_count == 1:
                # Data is single byte
                temp_c = round(bytes[2])
                temp_f = round((temp_c * 9/5) + 32, 1)
                humidity = round(bytes[0], 1)

            else:
                # Data is 2 bytes
                multiplier = 1  # Positive or negative temp multiplier

                if bytes[2] & 0b10000000:
                    multiplier = -1
                    bytes[2] = bytes[2] ^ 0b10000000

                temp_c =  round(multiplier * float(bytes[2] * 256 + bytes[3]) / 10, 1)
                temp_f = round((temp_c * 9/5) + 32, 1)
                humidity = round(float(bytes[0] * 256 + bytes[1]) / 10, 1)

        return {'temp_c': temp_c,
                'temp_f': temp_f,
                'humidity': humidity,
                'valid': valid}


    def __edge_callback(self, gpio, level, tick):

      hl_text = "HIGH" if level == 1 else "LOW"

      if self.__edge_count <= 1:
          if DHTXX.DEBUG: print(self.__edge_count, "RPI->DHT", "Request Data", hl_text)

      elif self.__edge_count <= 3:
          self.sensor_responded = True
          if DHTXX.DEBUG: print(self.__edge_count, "RPI<-DHT", "Transmission Starting", hl_text)

      elif self.__edge_count <= 4:
          # Initial data stream LOW
          if DHTXX.DEBUG: print(self.__edge_count, "RPI<-DHT", "Data", hl_text)

      elif self.__edge_count <= 84:
          if DHTXX.DEBUG: print(self.__edge_count, "RPI<-DHT", "Data", hl_text)

          elapsed = tick - self.__last_tick
          self.__last_tick = tick

          if level == 0:
              self.__bit_count += 1
              bit = 1 if elapsed >= 70 else 0
              self.data.append(bit)

              if DHTXX.DEBUG: print("  Elapsed microseconds={}, so data[{}]={}".format(elapsed, self.__bit_count, bit));

      else:
          self.__edge_callback_fn.cancel()
          self.read_success = len(self.data) == DHTXX.EXPECTED_DATA_BITS
          self.__c1 = self.__pi.get_current_tick()
          assert(level == pigpio.HIGH)  # GPIO is high when transmission is complete (sensor 'free' state per datasheet)
          assert(self.__edge_count == DHTXX.SUCCESS_EDGE_COUNT-1)

      self.__last_tick = tick
      self.__edge_count += 1

