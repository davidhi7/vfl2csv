import configparser
import json
from pathlib import Path

custom_converters = {'path': Path}

config = configparser.ConfigParser(converters=custom_converters)
config.read('config/config_vfl2csv.ini')

with open('config/columns.json', 'r') as file:
    column_layout = json.load(file)
