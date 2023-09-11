import configparser
import logging
from configparser import ConfigParser
from pathlib import Path

logger = logging.getLogger()


def get_config(config_path: Path | str, template: str = "") -> ConfigParser:
    if not isinstance(config_path, Path):
        config_path = Path(config_path)
    if not config_path.is_file():
        logger.info("Create new config file " + str(config_path.absolute()))
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, "w") as file:
            file.write(template)
    config = configparser.ConfigParser(converters={"path": Path})
    config.read(config_path, encoding="utf-8")
    return config
