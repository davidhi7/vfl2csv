import unittest
from pathlib import Path

import pandas as pd

from vfl2csv.input.ExcelInputSheet import ExcelInputSheet
from vfl2csv.input.ExcelWorkbook import ExcelWorkbook
from vfl2csv_base import test_config


class ExcelInputSheetTest(unittest.TestCase):

    def setUp(self) -> None:
        excel_workbook = ExcelWorkbook(Path(test_config['Input'].getpath('excel_sample_input_file')))
        self.sample_instance = ExcelInputSheet(excel_workbook, '09703_P2')

    def test_iterate_files(self):
        sheets = ExcelInputSheet.iterate_files(test_config['Input'].getpath('excel_sample_input_dir').glob('*.xlsx'))
        self.assertEqual(len(sheets), 17)

    def test_parse_dataframe(self):
        self.sample_instance.parse()
        df: pd.DataFrame = self.sample_instance.get_trial_site().df
        self.assertEqual(len(df.columns), 21)
        self.assertEqual(len(df), 468)
        values_count = df.count(axis='rows')
        for column in df.columns[3:]:
            self.assertEqual(len(column), 4)
            values_expected = int(column[3])
            self.assertEqual(values_count[column], values_expected)

    def test_parse_metadata(self):
        self.sample_instance.parse()
        metadata: dict = self.sample_instance.trial_site.metadata
        self.assertEqual(metadata, {
            "Forstamt": "5628   Bad Berka",
            "Revier": "Tiefborn",
            "Versuch": "09703",
            "Parzelle": "02",
            "Teilfläche": "2524 a3",
            "Standort": "Uf-K1",
            "Höhenlage": "420"
        })

    def test_str(self):
        self.assertEqual(str(self.sample_instance), str(Path('res/sample-data/excel/excel-1.xlsx')) + '#09703_P2')


if __name__ == '__main__':
    unittest.main()
