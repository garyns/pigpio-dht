import pytest
from pigpio_dht import DHT11, DHT22
from time import sleep

def test_dht22_data_parsing():
    #data22 = [0b00000010, 0b10010010, 0b00000001, 0b00001101, 0b10100010]
    data22 = [0,0,0,0,0,0,1,0, 1,0,0,1,0,0,1,0, 0,0,0,0,0,0,0,1, 0,0,0,0,1,1,0,1, 1,0,1,0,0,0,1,0]
   
    GPIO = 21 # GPIO for constructor, but never queried. 
    dht = DHT22(gpio=GPIO)
    dht.data = data22

    result = dht._parse_data()
    print(result)

    assert result['temp_c'] == 26.9
    assert result['temp_f'] == 80.4
    assert result['humidity'] == 65.8
    assert result['valid'] == True


def test_dht22_data_parsing_fail_checksum():
    #data22 = [0b00000010, 0b10010010, 0b00000001, 0b00001101, 0b10101111]
    data22 = [0,0,0,0,0,0,1,0, 1,0,0,1,0,0,1,0, 0,0,0,0,0,0,0,1, 0,0,0,0,1,1,0,1, 1,0,1,0,1,1,1,1]
    
    GPIO = 21 # GPIO for constructor, but never queried. 
    dht = DHT22(gpio=GPIO)
    dht.data = data22

    result = dht._parse_data()
    print(result)

    assert result['temp_c'] == 0
    assert result['temp_f'] == 0
    assert result['humidity'] == 0
    assert result['valid'] == False    


def test_dht22_negative_data_parsing():
    #data22 = [0b00000010, 0b10010010, 0b10000000, 0b01100101, 0b01111001]
    data22 = [0,0,0,0,0,0,1,0, 1,0,0,1,0,0,1,0, 1,0,0,0,0,0,0,0, 0,1,1,0,0,1,0,1, 0,1,1,1,1,0,0,1]

    GPIO = 21 # GPIO for constructor, but never queried. 
    dht = DHT22(gpio=GPIO)
    dht.data = data22

    result = dht._parse_data()
    print(result)

    assert result['temp_c'] == -10.1
    assert result['temp_f'] == 13.8
    assert result['humidity'] == 65.8
    assert result['valid'] == True

