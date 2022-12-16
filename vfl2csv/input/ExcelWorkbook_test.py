import io
import unittest

import openpyxl

from input.ExcelWorkbook import ExcelWorkbook
from test.testconfig import config


class ExcelWorkbookTest(unittest.TestCase):
    def test_constructor(self):
        workbook = ExcelWorkbook(config['Input'].getpath('excel_sample_input_file'))
        expected_sheets = ['09703_P2', '09703_P3', '11201_P11', '11201_P12', '11201_P13', '11201_P14', '11201_P21',
                           '11201_P22', '11201_P23', '11201_P24']
        self.assertEqual(workbook.path, config['Input'].getpath('excel_sample_input_file'))
        self.assertListEqual(workbook.sheets, expected_sheets)
        self.assertIsInstance(workbook.in_mem_file, io.BytesIO)
        self.assertIsInstance(workbook.open_workbook, openpyxl.Workbook)
        self.assertListEqual(workbook.open_workbook.sheetnames, expected_sheets)


if __name__ == '__main__':
    unittest.main()
