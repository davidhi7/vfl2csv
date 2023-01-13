import unittest

from vfl2csv import config, testconfig
from vfl2csv.batch_converter import validate, find_input_sheets


class BatchConverterTest(unittest.TestCase):

    def test_validate_arguments_validation(self):
        config.set('Input', 'input_format', 'Excel')
        self.assertRaises(ValueError, validate, ['vfl2csv_base'])
        self.assertRaises(ValueError, validate, ['vfl2csv_base', 'random_path_60I#h64B'])
        self.assertRaises(ValueError, validate, ['vfl2csv_base', 'random_path_60I#h64B', 'random_path_4w27NG@o'])
        # use two paths that definitely exist
        self.assertIsNone(validate(['vfl2csv_base', 'vfl2csv_base', 'vfl2csv_base']))

    def test_validate_basic_config_validation(self):
        config.set('Input', 'input_format', 'Excel')
        argv = ['vfl2csv_base', 'vfl2csv_base', 'vfl2csv_base']
        self.assertIsNone(validate(argv))
        config.set('Input', 'input_format', 'TSV')
        self.assertIsNone(validate(argv))
        config.set('Input', 'input_format', 'any other value')
        self.assertRaises(ValueError, validate, argv)

    def test_find_input_sheets_excel_file(self):
        config.set('Input', 'input_format', 'Excel')
        config.set('Input', 'input_file_extension', 'xlsx')
        input_files, input_trial_sheets = find_input_sheets(testconfig['Input'].getpath('excel_sample_input_file'))
        self.assertEqual(len(input_files), 1)
        self.assertEqual(len(input_trial_sheets), 10)

    def test_find_input_sheets_excel_dir(self):
        config.set('Input', 'input_format', 'Excel')
        config.set('Input', 'input_file_extension', 'xlsx')
        input_files, input_trial_sheets = find_input_sheets(testconfig['Input'].getpath('excel_sample_input_dir'))
        self.assertEqual(len(input_files), 2)
        self.assertEqual(len(input_trial_sheets), 17)

    def test_find_input_sheets_tsv_file(self):
        config.set('Input', 'input_format', 'TSV')
        config.set('Input', 'input_file_extension', 'txt')
        input_files, input_trial_sheets = find_input_sheets(testconfig['Input'].getpath('tsv_sample_input_file'))
        self.assertEqual(len(input_files), 1)
        self.assertEqual(len(input_trial_sheets), 1)

    def test_find_input_sheets_tsv_dir(self):
        config.set('Input', 'input_format', 'TSV')
        config.set('Input', 'input_file_extension', 'txt')
        input_files, input_trial_sheets = find_input_sheets(testconfig['Input'].getpath('tsv_sample_input_dir'))
        self.assertEqual(len(input_files), 6)
        self.assertEqual(len(input_trial_sheets), 6)


if __name__ == '__main__':
    unittest.main()
