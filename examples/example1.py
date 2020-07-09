# NOTE: The import has a _ not - in the module name.
from pigpio_dht import dht11, dht22

gpio = 21 # BCM Numbering

sensor = dht11(gpio)
#sensor = DHT22(gpio)

result = sensor.read()
print(result)