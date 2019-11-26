import pigpio
from time import time, sleep
from datetime import datetime

class DHT11:
  def __init__(self, gpio):
    self.gpio = gpio
    print("WIP")


if __name__ == "__main__":
  dht11 = DHT11(21)
