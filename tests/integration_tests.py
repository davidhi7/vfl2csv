import logging
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from subprocess import Popen

from openpyxl.cell import Cell, ReadOnlyCell
from openpyxl.cell.read_only import EmptyCell

from tests.ConversionAuditor import ConversionAuditor
from vfl2csv_base import config_factory, test_config
from vfl2csv_base.ColumnScheme import ColumnScheme

ExcelCell = Cell | ReadOnlyCell | EmptyCell

logger = logging.getLogger(__name__)
cwd = Path(__file__).parent.parent

config_path = Path('config/config_vfl2csv.ini')
config = config_factory.get_config(config_path)
column_scheme_path = Path('config/columns.json')
column_scheme = ColumnScheme.from_file(column_scheme_path)

auditor = ConversionAuditor(config, column_scheme)


def run_test(tmp_dir: Path, input_dir: Path):
    # Find input files manually
    file_paths = list(input_dir.glob(('**/' if config['Input'].getboolean('directory_search_recursively') else '') +
                                     f'*.{config["Input"]["input_file_extension"]}'))
    auditor.set_reference_files(file_paths)

    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_config = tmp_dir / 'config.ini'
    with open(tmp_config, 'x') as file:
        config.write(file)
    command = f'{sys.executable} -m vfl2csv ' \
              f'--column-scheme "{column_scheme_path}" ' \
              f'--config "{tmp_config}" ' \
              f'"{tmp_dir}" "{input_dir}" '
    print('>>> ' + command)
    proc = Popen(command, cwd=cwd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    proc.wait()
    for line in proc.stdout.readlines():
        print('> ' + line.decode('ascii'), end='')

    # Find all output metadata files by looking for them using the config file name pattern.
    # Replace all placeholders for metadata with asterisks
    metadata_file_pattern = re.sub(r'\{[^}]+}', '*', config['Output']['metadata_output_pattern'])
    metadata_files = list(tmp_dir.glob(metadata_file_pattern))
    auditor.audit_converted_metadata_files(metadata_files)


with tempfile.TemporaryDirectory() as tmp_dir:
    # First: Excel file conversion
    print('=== Run integration tests on Excel input ===')
    input_dir: Path = test_config['Input'].getpath('excel_sample_input_dir')
    config.set('Input', 'input_format', 'Excel')
    config.set('Input', 'input_file_extension', 'xlsx')
    run_test(Path(tmp_dir) / 'excel', input_dir)

    # Second: TSV file conversion
    print('=== Run integration tests on tab-delimited input ===')
    input_dir: Path = test_config['Input'].getpath('tsv_sample_input_dir')
    config.set('Input', 'input_format', 'TSV')
    config.set('Input', 'input_file_extension', 'txt')
    run_test(Path(tmp_dir) / 'tsv', input_dir)

    print('=== Completed without any errors ===')
