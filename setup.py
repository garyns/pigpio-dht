#from distutils.core import setup
from setuptools import setup, find_packages
import os.path

HERE = os.path.abspath(os.path.dirname(__file__))
README_PATH = os.path.join(HERE, 'README.rst')
try:
    README = open(README_PATH).read()
except IOError:
    README = ''

setup(
  name = 'pigpio-dht', 
  packages = ['pigpio_dht'],
  package_dir={'':'lib'},
  #packages=find_packages(),
  version = '0.3.1', 
  license = 'LGPL3',
  description = 'DHT11 & DHT22 Temperature and Humidity Sensor using pigpio',
  long_description = README,
  long_description_content_type = 'text/x-rst',
  author = 'Gary Smart',
  #author_email = "gary#at#smart-itc#dot#com#dot#au",
  url = 'https://github.com/garyns/pigpio-dht',
  download_url = 'https://github.com/garyns/pigpio-dht/archive/master.zip',
  keywords = ['DHT11', 'DHT22', 'pigpio', 'Raspberry Pi', 'RaspberryPi'],
  install_requires = [
          'pigpio'
      ],
  setup_requires = ['wheel'],
  classifiers=[
    'Development Status :: 4 - Beta',  # "3 - Alpha", "4 - Beta" or "5 - Production/Stable" 
    'Intended Audience :: Developers', 
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',  
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
