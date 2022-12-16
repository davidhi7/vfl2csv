import configparser
from pathlib import Path

config = configparser.ConfigParser(converters={'path': Path})
config.read('config.ini')
