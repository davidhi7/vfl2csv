from pathlib import Path

from vfl2csv_base import config_factory
from vfl2csv_base.ColumnScheme import ColumnScheme

config = config_factory.get_config(Path('config/config_vfl2csv.ini'))
testconfig = config_factory.get_config(Path('tests/test-config.ini'))
column_layout = ColumnScheme.from_file(Path('config/columns.json'))
