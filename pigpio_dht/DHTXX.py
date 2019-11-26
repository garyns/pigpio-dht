import pigpio
from time import time, sleep
from datetime import datetime

class DHTXX:

    DEBUG = False
    SUCCESS_EDGE_COUNT = 86
    EXPECTED_DATA_BITS = 40

    def __init__(self, gpio, timeout_secs=0.5, pi=None, datum_byte_count=1):
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
        self.__bit_count = -1
        self.__last_tick = -1
        self.__edge_count = -1

        self.__c0 = -1
        self.__c1 = -1

    def read(self, retry=True):
      
      result = self.__read()

      if result['valid'] == False:
          result = self.__read()

      return result


    def __read(self):

      self.__edge_count = 0
      self.read_success = False
      self.sensor_responded = False
      self.data = []
      self.__last_tick = self.__pi.get_current_tick()
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

        for i in range(0, len(self.data)):
          byte = byte << 1
          if (self.data[i]):
            byte = byte | 1
          else:
            byte = byte | 0

          if ((i + 1) % 8 == 0):
            bytes.append(byte)
            byte = 0

        valid = (bytes[0] + bytes[1] + bytes[2] + bytes[3]) == bytes[4]
        #valid = (bytes[0] + bytes[1] + bytes[2] + bytes[3] & 255) == bytes[4]

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
                temp_c = bytes[2]
                temp_f = int(temp_c * 9/5) + 32
                humidity = bytes[0]

            else:
                # Data is 2 bytes
                multiplier = 1  # Positive or negative temp multiplier

                if bytes[2] & 0b10000000:
                    multiplier = -1
                    bytes[2] = bytes[2] ^ 0b10000000

                temp_c =  multiplier * float(bytes[2] * 256 + bytes[3]) / 10
                temp_f = (temp_c * 9/5) + 32
                humidity = float(bytes[0] * 256 + bytes[1]) / 10

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

