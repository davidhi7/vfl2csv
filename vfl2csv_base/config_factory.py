import configparser
from configparser import ConfigParser
from pathlib import Path


def get_config(config_path: Path) -> ConfigParser:
    config = configparser.ConfigParser(converters={'path': Path})
    config.read(config_path)
    return config
