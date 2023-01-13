import unittest
from configparser import ConfigParser
from pathlib import Path

from vfl2csv_base.config_factory import get_config


class ConfigFactory(unittest.TestCase):
    sample_config_path = Path('tests/test-config.ini')

    def test_get(self) -> None:
        config = get_config(self.sample_config_path)
        self.assertIsInstance(config, ConfigParser)
        self.assertIsInstance(config['Input'].getpath('excel_sample_input_dir'), Path)


if __name__ == '__main__':
    unittest.main()
