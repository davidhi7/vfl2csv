from pathlib import Path

from vfl2csv_base import config_factory
from vfl2csv_base.input.ColumnLayout import ColumnLayout

config = config_factory.get_config(Path('config/config_vfl2csv.ini'))
testconfig = config_factory.get_config(Path('tests/test-config.ini'))
column_layout = ColumnLayout(Path('config/columns.json'))
