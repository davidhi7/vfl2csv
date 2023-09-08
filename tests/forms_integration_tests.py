import logging
import shutil
from pathlib import Path

import pandas as pd

import vfl2csv_forms
from vfl2csv_base import config_factory
from vfl2csv_base.ColumnScheme import ColumnScheme
from vfl2csv_gui.subsystems.forms.FormsConversionWorker import FormsConversionHandler
from vfl2csv_gui.subsystems.forms.FormsInputHandler import FormsInputHandler

logger = logging.getLogger(__name__)
cwd = Path(__file__).parent.parent

test_config = config_factory.get_config(cwd / Path('config/config_tests.ini'))
output_file: Path = cwd / test_config['Output'].getpath('temp_dir') / 'output.xlsx'
reference_file: Path = cwd / test_config['Input'].getpath('forms_reference_file')


def verify():
    output = pd.read_excel(output_file, sheet_name=None)
    reference = pd.read_excel(reference_file, sheet_name=None)
    if not reference.keys() == output.keys():
        logger.error(f'Output sheet names: {output.keys()}')
        logger.error(f'Reference sheet names: {reference.keys()}')
        raise ValueError("Output sheet names do not match reference sheet names")
    for sheet in reference.keys():
        if not output[sheet].equals(reference[sheet]):
            try:
                logger.error(output[sheet].compare(reference[sheet]))
            except ValueError:
                logger.error("Can't compare sheets because they have different column/row counts")
            raise ValueError("Output file contents don't match reference file contents")
    logger.info('Test succeeded')


if __name__ == '__main__':
    vfl2csv_forms.column_scheme = ColumnScheme.from_file(test_config['Input'].getpath('forms_test_columns_config'))
    output_file.parent.mkdir(parents=True, exist_ok=True)
    handler = FormsInputHandler()
    handler.load_input(test_config['Input']['forms_input_dir'])
    # We can't use handler.convert because it uses some qt logic
    FormsConversionHandler(handler.trial_sites, output_file).run()
    verify()
    shutil.rmtree(test_config['Output'].getpath('temp_dir'))
