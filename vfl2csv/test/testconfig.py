import configparser
from pathlib import Path

config = configparser.ConfigParser(converters={'path': Path})
config.read('tests/test-config.ini')
