from pathlib import Path

from vfl2csv_base.config_factory import get_config

testconfig = get_config(Path('tests/test-config.ini'))
