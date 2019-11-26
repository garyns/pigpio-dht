from DHTXX import DHTXX
import sys

class DHT11(DHTXX):
     def __init__(self, gpio, timeout_secs=0.5, pi=None):
         # for DHT11 datum_byte_count = 1 
         super(DHT11, self).__init__(gpio, timeout_secs, pi, datum_byte_count=1)

if __name__ == "__main__":

    if len(sys.argv) == 2:
        gpio = int(sys.argv[1])
        sensor = DHT11(gpio)
        print(sensor.read())
    else:
        print("Usage: " + sys.argv[0] + " <BCM GPIO>")


