import shutil
import tempfile
import unittest
from pathlib import Path

from vfl2csv import config
from vfl2csv.batch_converter import find_input_sheets
from vfl2csv_base import test_config


class BatchConverterTest(unittest.TestCase):

    def test_find_input_sheets_excel_file(self):
        config.set('Input', 'input_format', 'Excel')
        config.set('Input', 'input_file_extension', 'xlsx')
        input_files, input_trial_sheets = find_input_sheets(test_config['Input'].getpath('excel_sample_input_file'))
        self.assertEqual(len(input_files), 1)
        self.assertEqual(len(input_trial_sheets), 10)

    def test_find_input_sheets_excel_dir(self):
        config.set('Input', 'input_format', 'Excel')
        config.set('Input', 'input_file_extension', 'xlsx')
        input_files, input_trial_sheets = find_input_sheets(test_config['Input'].getpath('excel_sample_input_dir'))
        self.assertEqual(len(input_files), 2)
        self.assertEqual(len(input_trial_sheets), 17)

    def test_find_input_sheets_tsv_file(self):
        config.set('Input', 'input_format', 'TSV')
        config.set('Input', 'input_file_extension', 'txt')
        input_files, input_trial_sheets = find_input_sheets(test_config['Input'].getpath('tsv_sample_input_file'))
        self.assertEqual(len(input_files), 1)
        self.assertEqual(len(input_trial_sheets), 1)

    def test_find_input_sheets_tsv_dir(self):
        config.set('Input', 'input_format', 'TSV')
        config.set('Input', 'input_file_extension', 'txt')
        input_files, input_trial_sheets = find_input_sheets(test_config['Input'].getpath('tsv_sample_input_dir'))
        self.assertEqual(len(input_files), 6)
        self.assertEqual(len(input_trial_sheets), 6)

    def test_find_input_sheets_from_list(self):
        config.set('Input', 'input_format', 'TSV')
        config.set('Input', 'input_file_extension', 'txt')
        input_files, input_trial_sheets = find_input_sheets([test_config['Input'].getpath('tsv_sample_input_dir')] * 2)
        self.assertEqual(len(input_files), 12)
        self.assertEqual(len(input_trial_sheets), 12)

    def test_find_input_sheets_recursive_discovery(self):
        config.set('Input', 'input_format', 'TSV')
        config.set('Input', 'input_file_extension', 'txt')
        config.set('Input', 'directory_search_recursively', "true")
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(
                src=test_config['Input'].getpath('tsv_sample_input_dir'),
                dst=Path(tmp) / 'test'
            )
            input_files, input_trial_sheets = find_input_sheets(Path(tmp))
            self.assertEqual(len(input_files), 6)
            self.assertEqual(len(input_trial_sheets), 6)

            config.set('Input', 'directory_search_recursively', "false")
            input_files, input_trial_sheets = find_input_sheets(Path(tmp))
            self.assertEqual(len(input_files), 0)
            self.assertEqual(len(input_trial_sheets), 0)


if __name__ == '__main__':
    unittest.main()
