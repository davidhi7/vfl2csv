import unittest
from pathlib import Path

import pandas as pd

from vfl2csv import testconfig
from vfl2csv.input.TsvInputFile import TsvInputFile


class TsvInputFileTest(unittest.TestCase):

    def setUp(self) -> None:
        self.sample_instance = TsvInputFile(Path(testconfig['Input'].getpath('tsv_sample_input_file')))

    def test_iterate_files(self):
        sheets = TsvInputFile.iterate_files(testconfig['Input'].getpath('tsv_sample_input_dir').glob('*.txt'))
        self.assertEqual(len(sheets), 6)

    def test_parse_dataframe(self):
        self.sample_instance.parse()
        df: pd.DataFrame = self.sample_instance.get_trial_site().df
        self.assertEqual(len(df.columns), 15)
        self.assertEqual(len(df), 159)
        values_count = df.count(axis='rows')
        for column in df.columns[3:]:
            self.assertEqual(len(column), 4)
            values_expected = int(column[3])
            self.assertEqual(values_count[column], values_expected)

    def test_parse_metadata(self):
        self.sample_instance.parse()
        metadata: dict = self.sample_instance.trial_site.metadata
        self.assertEqual(metadata, {
            "Forstamt": "44   Schönheide",
            "Revier": "Hundshübel",
            "Versuch": "14607",
            "Parzelle": "01",
            "Teilfläche": "112 a2",
            "Standort": "Mf-Z3",
            "Höhenlage": "680"
        })

    def test_str(self):
        self.assertEqual(str(self.sample_instance), 'res/sample-data/tab-delimited/1460701.txt')


if __name__ == '__main__':
    unittest.main()
