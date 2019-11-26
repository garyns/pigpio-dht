import pigpio
from time import time, sleep
from datetime import datetime

class DHT11:

    def __init__(self, gpio, timeout_secs=0.5, pi=None):

        self.gpio = gpio
        self.timeout_secs = timeout_secs
        self.read_success = False
        self.data = []

        if pi != None:
            self.__pi = pi
        else:
            self.__pi = pigpio.pi()

        self.__pi.set_pull_up_down(gpio, pigpio.PUD_UP)

        self.__bit_count = -1
        self.__last_tick = -1
        self.__edge_count = -1

        self.__c0 = -1
        self.__c1 = -1


    def read(self):

      self.__edge_count = 0
      self.read_success = False
      self.data = []
      self.__last_tick = self.__pi.get_current_tick()
      self.__c0 = self.__last_tick

      self.__edge_callback_fn = self.__pi.callback(self.gpio, pigpio.EITHER_EDGE, self.__edge_callback)

      self.__pi.set_mode(self.gpio, pigpio.OUTPUT)
      self.__pi.write(self.gpio, pigpio.LOW)
      sleep(0.018)  # 18ms as per DHT11/22 datasheet
      self.__pi.write(self.gpio, pigpio.HIGH)

      self.__pi.set_mode(self.gpio, pigpio.INPUT)

      sleep(self.timeout_secs)
      print("Read Success?", self.read_success)
      self.__edge_callback_fn.cancel()

      elapsed_secs = (self.__c1 - self.__c0) / 1000000
      print("Round Trip Secs:", elapsed_secs)

      return self.__parse_data()

    def __parse_data(self):
        #self.data = [0,0,0,0,0,0,1,0,1,0,0,1,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1,1,0,1,1,0,1,0,0,0,1,0]
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

        valid = (bytes[0] + bytes[1] + bytes[2] + bytes[3] & 255) == bytes[4]

        print("len(data) =", len(self.data))
        print("data =", self.data)
        print("bytes =", bytes)

        temp_c_v1 = bytes[2] + bytes[3]/256

        neg_mask = 0b10000000
        multiplier = 1
        if bytes[2] & neg_mask:
          multiplier = -1
          bytes[2] = bytes[2] ^ neg_mask

        temp_c =  multiplier * float(bytes[2] * 256 + bytes[3]) / 10

        return {'temp_c_v1': temp_c_v1,
                'temp_c': temp_c,
                #'temp_f': (temp_c * 9/5) + 32,
                'humidity_v1': bytes[0] + bytes[1]/256,
                'humidity': float(bytes[0] * 256 + bytes[1]) / 10,
                'checksum': bytes[4],
                'valid': valid}

    def __parse_data_v1(self):
        bytes = []
        byte = 0

        for i in range(0, len(self.data)):
          byte = byte << 1
          if (self.data[i]):
            byte = byte | 1
          else:
            byte = byte | 0

          print(i,byte)
          if ((i + 1) % 8 == 0):
            bytes.append(byte)
            byte = 0

        valid = (bytes[0] + bytes[1] + bytes[2] + bytes[3] & 255) == bytes[4]

        print("len(data) =", len(self.data))
        print("data =", self.data)
        print("bytes =", bytes)

        temp_c = bytes[2] + bytes[3]/256
        return {'temp_c':  temp_c,
                'temp_f': (temp_c * 9/5) + 32,
                'humidity': bytes[0] + bytes[1]/256 ,
                'checksum': bytes[4],
                'valid': valid}

    def __edge_callback(self, gpio, level, tick):

      hl_text = "HIGH" if level == 1 else "LOW"

      if self.__edge_count <= 1:
          print(self.__edge_count, "RPI->DHT", "Request Data", hl_text)

      elif self.__edge_count <= 3:
          print(self.__edge_count, "RPI<-DHT", "Transmission Starting", hl_text)

      elif self.__edge_count <= 4:

          print(self.__edge_count, "RPI<-DHT", "Data", hl_text)

      elif self.__edge_count <= 84:

          elapsed = tick - self.__last_tick

          print(self.__edge_count, "RPI<-DHT", "Data", hl_text)
          self.__last_tick = tick

          if level == 0:
              bit = 1 if elapsed >= 70 else 0
              print("Elapsed microseconds={}, so data[{}]={}".format(elapsed, self.__bit_count, bit));
              self.data.append(bit)
              self.__bit_count += 1

      else:
          print(self.__edge_count, "END ON HIGH", level)
          assert (level == pigpio.HIGH)
          self.__edge_callback_fn.cancel()
          self.read_success = True
          self.__c1 = self.__pi.get_current_tick()

      self.__last_tick = tick
      self.__edge_count += 1


if __name__ == "__main__":
  dht11 = DHT11(21)
