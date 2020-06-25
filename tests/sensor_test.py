import pytest
from pigpio_dht import DHT11, DHT22
from time import sleep

# Time for sensor to settle between multiple tests.
sleep(2)

dht11_result = {}
dht22_result = {}


def test_dht11(dht11gpio):

    if not dht11gpio:
        pytest.skip("Skipping. No GPIO Pin for DHT11 Provided.")
        return

    dht = DHT11(gpio=int(dht11gpio))
    result = dht.read()
    print(result)

    dht11_result = result

    assert 'temp_c' in result
    assert 'temp_f' in result
    assert 'humidity' in result
    assert 'valid' in result
    assert 0 <= result['humidity'] <= 100

def test_dht22(dht22gpio):

    if not dht22gpio:
        pytest.skip("Skipping. No GPIO Pin for DHT22 Provided.")
        return

    dht = DHT22(gpio=int(dht22gpio))
    result = dht.read()
    print(result)
    
    dht22_result = result

    assert 'temp_c' in result
    assert 'temp_f' in result
    assert 'humidity' in result
    assert 'valid' in result
    assert 0 <= result['humidity'] <= 100
