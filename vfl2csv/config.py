import configparser
import json
from pathlib import Path

custom_converters = {'path': Path}

config = configparser.ConfigParser(converters=custom_converters)
testconfig = configparser.ConfigParser(converters=custom_converters)
config.read('config/config.ini')
testconfig.read('tests/test-config.ini')

with open('config/columns.json', 'r') as file:
    column_layout = json.load(file)
