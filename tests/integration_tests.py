import logging
import sys
import tempfile
from pathlib import Path
from subprocess import Popen

from openpyxl.cell import Cell, ReadOnlyCell
from openpyxl.cell.read_only import EmptyCell

from tests.ConversionAudit import ConversionAudit
from vfl2csv_base import config_factory, test_config
from vfl2csv_base.ColumnScheme import ColumnScheme

ExcelCell = Cell | ReadOnlyCell | EmptyCell

logger = logging.getLogger(__name__)

cwd = Path(__file__).parent.parent

config_path = Path('config/config_vfl2csv.ini')
column_scheme_path = Path('config/columns.json')
config = config_factory.get_config(config_path)
column_scheme = ColumnScheme.from_file(column_scheme_path)

config.set('Input', 'input_format', 'Excel')
config.set('Input', 'input_file_extension', 'xlsx')
input_dir: Path = test_config['Input'].getpath('excel_sample_input_dir')
with tempfile.TemporaryDirectory() as tmp_dir:
    # Find input files manually
    file_paths = list(input_dir.glob(('**/' if config['Input'].getboolean('directory_search_recursively') else '') +
                                     f'*.{config["Input"]["input_file_extension"]}'))

    auditor = ConversionAudit(config, column_scheme)
    auditor.set_reference_files(file_paths, config['Input']['input_format'])

    # Run tests with Excel input
    excel_config_path = Path(tmp_dir) / 'config-xlsx.ini'
    with open(excel_config_path, 'w') as file:
        config.write(file)
    command = f'{sys.executable} -m vfl2csv --column-scheme {column_scheme_path} --config {excel_config_path} {tmp_dir} {input_dir}'
    logger.info(f'Execute command "{command}"')
    Popen(command, cwd=cwd).wait()

    metadata_files = list(Path(tmp_dir).rglob('**/*_metadata.txt'))
    auditor.audit_converted_metadata_files(metadata_files)
    logger.info('done')
