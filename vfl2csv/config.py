import configparser
from pathlib import Path

custom_converters = {'path': Path}

config = configparser.ConfigParser(converters=custom_converters)
testconfig = configparser.ConfigParser(converters=custom_converters)
config.read('config.ini')
testconfig.read('tests/test-config.ini')
