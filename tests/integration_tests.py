import argparse
import logging
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from subprocess import Popen

from tests.ConversionAuditor import ConversionAuditor
from vfl2csv_base import config_factory, test_config
from vfl2csv_base.ColumnScheme import ColumnScheme

logger = logging.getLogger(__name__)
cwd = Path(__file__).parent.parent

config = config_factory.get_config(Path('config/config_vfl2csv.ini'))
column_scheme_path = test_config['Input'].getpath('vfl2csv_test_columns_config')
column_scheme = ColumnScheme.from_file(column_scheme_path)

auditor = ConversionAuditor(config, column_scheme)

parser = argparse.ArgumentParser(
    prog='integration_tests',
    description='Run integration tests on vfl2csv'
)
parser.add_argument(
    '--executable', '-x',
    action='store',
    default=f'{sys.executable} -m vfl2csv',
    help='specify a custom executable to test'
)
arguments = vars(parser.parse_args())


def run_test(tmp_dir: Path, input_dir: Path):
    # Find input files manually
    file_paths = list(input_dir.glob(('**/' if config['Input'].getboolean('directory_search_recursively') else '') +
                                     f'*.{config["Input"]["input_file_extension"]}'))
    auditor.set_reference_files(file_paths)

    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_config = tmp_dir / 'config.ini'
    with open(tmp_config, 'x') as file:
        config.write(file)
    command = arguments['executable'] + \
              f' --column-scheme "{column_scheme_path}"' \
              f' --config "{tmp_config}"' \
              f' "{tmp_dir}" "{input_dir}"'
    print('>>> ' + command)
    proc = Popen(command, cwd=cwd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    proc.wait()

    for line in proc.stdout.readlines():
        print('> ' + line.decode('ascii'), end='')

    if proc.returncode != 0:
        raise ValueError(f'Return code {proc.returncode} instead of 0')

    # Find all output metadata files by looking for them using the config file name pattern.
    # Replace all placeholders for metadata with asterisks
    metadata_file_pattern = re.sub(r'\{[^}]+}', '*', config['Output']['metadata_output_pattern'])
    metadata_files = list(tmp_dir.glob(metadata_file_pattern))
    if len(metadata_files) == 0:
        raise ValueError('No metadata files found')
    auditor.audit_converted_metadata_files(metadata_files)


with tempfile.TemporaryDirectory() as tmp_dir:
    tmp_dir_path = Path(tmp_dir)
    # Excel file conversion
    print('=== Run integration tests on Excel input ===')
    input_dir: Path = test_config['Input'].getpath('excel_sample_input_dir')
    config.set('Input', 'input_format', 'Excel')
    config.set('Input', 'input_file_extension', 'xlsx')
    config.set('Multiprocessing', 'enabled', 'False')
    run_test(tmp_dir_path / 'excel', input_dir)

    # TSV file conversion
    print('=== Run integration tests on tab-delimited input ===')
    input_dir: Path = test_config['Input'].getpath('tsv_sample_input_dir')
    config.set('Input', 'input_format', 'TSV')
    config.set('Input', 'input_file_extension', 'txt')
    config.set('Multiprocessing', 'enabled', 'False')
    run_test(tmp_dir_path / 'tsv', input_dir)

    # Excel files with multiprocessing
    print('=== Run integration tests using multiprocessing ===')
    input_dir: Path = test_config['Input'].getpath('excel_sample_input_dir')
    config.set('Input', 'input_format', 'Excel')
    config.set('Input', 'input_file_extension', 'xlsx')
    config.set('Multiprocessing', 'enabled', 'True')
    config.set('Multiprocessing', 'sheets_per_core', '1')
    run_test(tmp_dir_path / 'mp-excel', input_dir)

    # TSV files with multiprocessing
    print('=== Run integration tests using multiprocessing ===')
    input_dir: Path = test_config['Input'].getpath('tsv_sample_input_dir')
    config.set('Input', 'input_format', 'TSV')
    config.set('Input', 'input_file_extension', 'txt')
    config.set('Multiprocessing', 'enabled', 'True')
    config.set('Multiprocessing', 'sheets_per_core', '1')
    run_test(tmp_dir_path / 'mp-tsv', input_dir)

    print('=== Completed without any exceptions ===')
