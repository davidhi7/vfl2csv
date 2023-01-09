from pathlib import Path

import config_factory

testconfig = config_factory.get_config(Path('tests/test-config.ini'))
