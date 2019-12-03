from .DHTXX import DHTXX
import sys

"""
DHT22 Temperature and Humidity Sensor
"""
class DHT22(DHTXX):

    def __init__(self, gpio, timeout_secs=0.5, use_internal_pullup=True, pi=None):
        """
        DHT22 Constructor

        :param gpio: BCM Pin of sensor
        :type gpio: Integer
        :param timeout_secs: sensor read timeout in seconds
        :type timeout_secs: integer
        :param use_internal_pullup: use internal pull-up resistor on data gpio
        :type use_internal_pullup: boolean
        :param pi: Custom instance of pigpio.pi()
        :type pi: pigpio
        """

        # for DHT22 datum_byte_count = 2, max_read_rate_secs = 2
        super(DHT22, self).__init__(gpio, pi=pi, timeout_secs=timeout_secs, use_internal_pullup=True, max_read_rate_secs=2, datum_byte_count=2)


if __name__ == "__main__":

    if len(sys.argv) == 2:
        gpio = int(sys.argv[1])
        sensor = DHT22(gpio)
        print(sensor.read())
    else:
        print("Usage: " + sys.argv[0] + " <BCM GPIO>")


