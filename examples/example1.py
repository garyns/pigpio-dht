# NOTE: The import has a _ not - in the module name.
from pigpio_dht import DHT11, DHT22

gpio = 21 # BCM Numbering

sensor = DHT11(gpio)
#sensor = DHT22(gpio)

result = sensor.read()
print(result)
