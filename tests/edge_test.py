import pigpio
import pytest
from time import time, sleep

EXPECTED_SUCCESS_EDGE_COUNT = 86

pi = pigpio.pi()

timeout_secs = 0.5
pause_secs = 2
edge_count = 0

def edge_callback(gpio, level, tick):
    global edge_count
    edge_count += 1
    #print(edge_count)


def test_count_edges_dht11(dht11gpio):
    if not dht11gpio:
        pytest.skip("Skipping. No GPIO Pin for DHT11 Provided.")
        return

    do_count(dht11gpio)


def test_count_edges_dht22(dht22gpio):
    if not dht22gpio:
        pytest.skip("Skipping. No GPIO Pin for DHT22 Provided.")
        return

    do_count(dht22gpio)


def count(gpio):
    global edge_count
    edge_count = 0

    edge_callback_fn = pi.callback(gpio, pigpio.EITHER_EDGE, edge_callback)

    pi.set_mode(gpio, pigpio.OUTPUT)
    pi.write(gpio, pigpio.LOW)
    sleep(0.018)  # 18ms pause as per datasheet
    
    pi.set_mode(gpio, pigpio.INPUT)

    sleep(timeout_secs) # Timeout
    print("Timeout")

    edge_callback_fn.cancel()
    print("Edge Count", edge_count)
    assert edge_count == EXPECTED_SUCCESS_EDGE_COUNT



def do_count(gpio):
    for _ in range(10):
        count(gpio)
        sleep(pause_secs)


