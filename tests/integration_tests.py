import logging
import sys
import tempfile
from pathlib import Path
from subprocess import Popen

from vfl2csv import config
from vfl2csv_base import test_config

logger = logging.getLogger(__name__)

executable = sys.executable
cwd = Path(__file__).parent.parent

config_path = Path('tests/test_config_vfl2csv.ini')
column_scheme_path = Path('tests/test-columns.json')

# Run tests with Excel input
input_dir = test_config['Input']['excel_sample_input_dir']
with tempfile.TemporaryDirectory() as tmp_dir:
    config.set('Input', 'input_format', 'Excel')
    config.set('Input', 'input_file_extension', 'xlsx')
    command = f'{executable} -m vfl2csv --column-scheme {column_scheme_path} {tmp_dir} {input_dir}'
    logger.info(f"Execute command '{command}'")
    Popen(command, cwd=cwd)
