pigpio-dht
==========

DHT11 and DHT22 Driver Library based on the pigpio_ GPIO library.

.. _pigpio: http://www.python.org/


Installation
------------

``pip install pigpio-dht``

Supported Versions of Python
----------------------------

Tested against Python >= 3.5.

It may work with other earlier versions but this has not been confirmed.

Links
-----

- `GitHub Repository`_

.. _GitHub Repository : https://github.com/garyns/pigpio-dht

DHT Sensors are Slow
--------------------

DHT sensors are slow to take readings, and need to settle between reads. For instance, the maximum read rates for the sensors are:

- DHT11 once every 1 seconds
- DHT22 once every 2 seconds

This library monitors the read rate and will pause between successive calls to ``read()`` to honor these limits.


Examples
--------

One-Shot Read
*************

Take a single reading from the sensor.

Code
^^^^
::

  from pigpio-dit import DHT11, DHT22

  gpio = 21 # BCM Numbering

  sensor = DHT11(gpio)
  #sensor = DHT22(gpio)

  result = sensor.read()
  print(result)

Output
^^^^^^
::

  {'temp_c': 20, 'temp_f': 68.0, 'humidity': 35, 'valid': True}

Also see
^^^^^^^^

`read()`__

__ `read(retries=0) raises TimeoutError`_


Sampled Read
************

Take many readings (by repeating calling ``read()``) from the sensor and return a normalised result.

Code
^^^^

::

  from pigpio-dit import DHT11, DHT22

  gpio = 21 # BCM Numbering

  sensor = DHT11(gpio)
  #sensor = DHT22(gpio)

  result = sensor.sample(samples=5)
  print(result)

Output
^^^^^^

::

  {'temp_c': 20, 'temp_f': 68.0, 'humidity': 35, 'valid': True}

Also see
^^^^^^^^

`sample()`__

__ `sample(samples=5, max_retries=None) raises TimeoutError`_

API 
---

The classes ``DHT11`` and ``DHT22`` both extend the base class ``DHTXX`` and share a common the API.

Constructor: DHT11 | DHT22(gpio, timeout_secs=0.5, use_internal_pullup=True, pi=None)
*************************************************************************************

Parameters
^^^^^^^^^^

- **gpio** GPIO (BCM) pin that data leg of sensor is connected to
- **timeout_secs** Sensor timeout in second. Default should be adequate unless you receive a TimeoutError advising you to increase the value wuth calling ``read()`` or ``sample()``
- **use_internal_pullup** - Enable internal pull-up resistor on gpio
- **pi** a custom instance of ``pigpio.pi()``

read(retries=0) raises TimeoutError
************************************

Take a single reading from the sensor.

Parameters
^^^^^^^^^^

- **retries** number of times to keep retrying when the result contains ``valid = False``

Returns
^^^^^^^
A Dictionary in the form ``{'temp_c': 20, 'temp_f': 68.0, 'humidity': 35, 'valid': True}``

Where:

- **temp_c** is the temperature in degrees Celsius
- **temp_f** is the temperature in degrees Fahrenheit
- **humidity** is the relative humidity
- **valid** is true only if sensors checksum matches with returned data.

**Discard readings where** ``value == False`` **and try again.**


Raises
^^^^^^

TimeoutError
""""""""""""

- If the sensor on ``gpio`` does not respond
- If the sensor responds within ``timeout_secs`` (see _Constructor), but the response cannot be understood by the library. Try increasing ``timeout_secs``

Also see
^^^^^^^^

`DHT Sensors are Slow`_

sample(samples=5, max_retries=None) raises TimeoutError
*******************************************************

Take many readings (by repeating calling ``read()``) from the sensor and return a normalised result.

Please note that a call to ``sample()`` takes time. For example for the DHT11 with a maximum read rate of once every 1 seconds, 5 samples will take approximately 1 second * 5 samples = 5 seconds.

**Parameters:**

- **samples** number of samples to take
- **max_retries** maximum number of times to keep retrying *per sample* when the result contains ``valid = False``. Default to samples * 2

Raises
^^^^^^

TimeoutError
""""""""""""

- Same as for ``read()``, *plus*
- If ``max_retries`` is reached

