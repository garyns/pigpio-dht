from ..src import DHT11, DHT22

print("\n\nDATA 22")
data22 = [0b00000010, 0b10010010, 0b00000001, 0b00001101, 0b10100010]
humidity = float(data22[0]*256 + data22[1]) / 10
print("65.8%RH=", humidity)
assert(humidity == 65.8)

temp_c = float(data22[2]*256 + data22[3]) / 10
print("26.0'C=", temp_c)
assert(temp_c == 26.9)

# negative temp.
neg_mask = 0b10000000
data22 = [-1, -1, 0b10000000, 0b01100101]

multiplier = 1
if data22[2] & neg_mask:
    multiplier = -1
    data22[2] = data22[2] ^ neg_mask

temp_c = multiplier * float(data22[2]*256 + data22[3]) / 10
print("-10.1'C=", temp_c)
assert(temp_c == -10.1)


print("\n\nDATA 11")
data11 = [32, 0, 21, 0, 53]
data11 = data22
temp_c = round(data11[2])
humidity = round(data11[0], 1)
print("21'C=", temp_c)
print("32%RH=", humidity)


def test_dht11_data_parsing():
    data11 = [32, 0, 21, 0, 53]

    dht = DHT11(gpio=0) # Dummy GPIO
    dht.data = data11

    result = dht.__parse_data()
    print(result)

    assert result['temp_c'] == 21.0
    #assert result['temp_f'] ==
    assert result['humidity'] == 32.0
    assert result['valid'] == True



def test_dht12_data_parsing():

    data22 = [0b00000010, 0b10010010, 0b00000001, 0b00001101, 0b10100010]

    dht = DHT22(gpio=0) # Dummy GPIO
    dht.data = data22

    result = dht.__parse_data()
    print(result)

    assert result['temp_c'] == 26.9
    #assert result['temp_f'] ==
    assert result['humidity'] == 65.8
    assert result['valid'] == True


def test_dht12_negative_data_parsing():

    data22 = TODO

    dht = DHT22(gpio=0) # Dummy GPIO
    dht.data = data22

    result = dht.__parse_data()
    print(result)

    assert result['temp_c'] == 26.9
    #assert result['temp_f'] ==
    assert result['humidity'] == 65.8
    assert result['valid'] == True


