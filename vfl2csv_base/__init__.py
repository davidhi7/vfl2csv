from pathlib import Path

from .config_factory import get_config

testconfig = get_config(Path('tests/test-config.ini'))
