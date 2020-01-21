import pytest

def pytest_addoption(parser):
    parser.addoption("--dht11gpio", action="store", default=None)
    parser.addoption("--dht22gpio", action="store", default=None)

@pytest.fixture
def dht11gpio(request):
    gpio = request.config.getoption("dht11gpio")
    if gpio:
      return int(gpio)

@pytest.fixture
def dht22gpio(request):
    gpio = request.config.getoption("dht22gpio")
    if gpio:
      return int(gpio)


