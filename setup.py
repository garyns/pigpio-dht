#from distutils.core import setup
from setuptools import setup
import os.path

HERE = os.path.abspath(os.path.dirname(__file__))
README_PATH = os.path.join(HERE, 'README.md')
try:
    README = open(README_PATH).read()
except IOError:
    README = ''

setup(
  name = 'pigpio-dht', 
  packages = ['pigpio_dht'],
  version = '0.2.1', 
  license = 'LGPL3', 
  description = 'DIT11 Temperature and Humidity Sensor using pigpio',
  long_description = README,
  author = 'Gary Smart',
  #author_email = 'no_spam@domain.com',
  url = 'https://github.com/garyns/pigpio-dht',
  download_url = 'https://github.com/garyns/pigpio-dht/archive/master.zip',
  keywords = ['DHT11', 'DHT22', 'pigpio'],
  install_requires=[ 
          'pigpio'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" 
    'Intended Audience :: Developers', 
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',  
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
