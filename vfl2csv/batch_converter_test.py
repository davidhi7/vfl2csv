import shutil
import tempfile
import unittest
from pathlib import Path

from vfl2csv import setup
from vfl2csv.batch_converter import find_input_data
from vfl2csv.input.ExcelInputSheet import ExcelInputSheet
from vfl2csv_base import test_config


class BatchConverterTest(unittest.TestCase):

    def test_find_input_sheets_excel_file(self):
        setup.config.set('Input', 'input_format', 'Excel')
        setup.config.set('Input', 'input_file_extension', 'xlsx')
        input_files, input_trial_sheets = find_input_data(test_config['Input'].getpath('excel_sample_input_file'))
        input_trial_sheets: list[ExcelInputSheet]
        self.assertEqual(len(input_files), 1)
        self.assertEqual(len(input_trial_sheets), 10)
        self.assertCountEqual([sheet.sheet_name for sheet in input_trial_sheets], [
            '09703_P2', '09703_P3', '11201_P11', '11201_P12', '11201_P13', '11201_P14', '11201_P21', '11201_P22',
            '11201_P23', '11201_P24'
        ])

    def test_find_input_sheets_excel_dir(self):
        setup.config.set('Input', 'input_format', 'Excel')
        setup.config.set('Input', 'input_file_extension', 'xlsx')
        input_files, input_trial_sheets = find_input_data(test_config['Input'].getpath('excel_sample_input_dir'))
        input_trial_sheets: list[ExcelInputSheet]
        self.assertEqual(len(input_files), 2)
        self.assertEqual(len(input_trial_sheets), 17)
        self.assertCountEqual([sheet.sheet_name for sheet in input_trial_sheets], [
            '09703_P2', '09703_P3', '11201_P11', '11201_P12', '11201_P13', '11201_P14', '11201_P21', '11201_P22',
            '11201_P23', '11201_P24', '09201_518a2', '09202_536a3', '09702_P1', '09702_P2', '09702_P3', '09702_P4',
            '09703_P1'
        ])

    def test_find_input_sheets_tsv_file(self):
        setup.config.set('Input', 'input_format', 'TSV')
        setup.config.set('Input', 'input_file_extension', 'txt')
        input_files, input_trial_sheets = find_input_data(test_config['Input'].getpath('tsv_sample_input_file'))
        self.assertEqual(len(input_files), 1)
        self.assertEqual(len(input_trial_sheets), 1)

    def test_find_input_sheets_tsv_dir(self):
        setup.config.set('Input', 'input_format', 'TSV')
        setup.config.set('Input', 'input_file_extension', 'txt')
        input_files, input_trial_sheets = find_input_data(test_config['Input'].getpath('tsv_sample_input_dir'))
        self.assertEqual(len(input_files), 6)
        self.assertEqual(len(input_trial_sheets), 6)

    def test_find_input_sheets_from_list(self):
        setup.config.set('Input', 'input_format', 'TSV')
        setup.config.set('Input', 'input_file_extension', 'txt')
        input_files, input_trial_sheets = find_input_data([test_config['Input'].getpath('tsv_sample_input_dir')] * 2)
        self.assertEqual(len(input_files), 12)
        self.assertEqual(len(input_trial_sheets), 12)

    def test_find_input_sheets_recursive_discovery(self):
        setup.config.set('Input', 'input_format', 'TSV')
        setup.config.set('Input', 'input_file_extension', 'txt')
        setup.config.set('Input', 'directory_search_recursively', "true")
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(
                src=test_config['Input'].getpath('tsv_sample_input_dir'),
                dst=Path(tmp) / 'test'
            )
            input_files, input_trial_sheets = find_input_data(Path(tmp))
            self.assertEqual(len(input_files), 6)
            self.assertEqual(len(input_trial_sheets), 6)

            setup.config.set('Input', 'directory_search_recursively', "false")
            input_files, input_trial_sheets = find_input_data(Path(tmp))
            self.assertEqual(len(input_files), 0)
            self.assertEqual(len(input_trial_sheets), 0)

    def test_findInputSheets_input_format_validation(self):
        setup.config.set('Input', 'input_format', 'illegal value')
        self.assertRaises(ValueError, find_input_data, Path('/this/path/does/not/exist'))


if __name__ == '__main__':
    unittest.main()
