from distutils.core import setup
setup(
  name = 'pigpio-dht', 
  packages = ['piopio.dht'],
  version = '0.1', 
  license='GNU GPL v3', 
  description = 'DIT11 Temperature and Humidity Sensor using pigpio',
  author = 'Gary smart',
  author_email = 'no_spam@domain.com',
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
    'License :: OSI Approved :: GNU GPL v3 License', 
    'Programming Language :: Python :: 3',  
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
