import logging
from pathlib import Path

from vfl2csv_base import config_factory
from ColumnScheme import ColumnScheme

logging.basicConfig(format='%(levelname)s %(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

config = config_factory.get_config(Path('config/config_forms.ini'))
column_scheme = ColumnScheme.from_file(Path('config/columns.json'))
