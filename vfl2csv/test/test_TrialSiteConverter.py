import filecmp
import io
import shutil
import unittest
from pathlib import Path

import openpyxl
import pandas as pd


class TestTrialSiteSheet(unittest.TestCase):
    test_resources = Path('res/test')
    temp_dir = test_resources / 'tmp'
    test_filename = test_resources / 'test_data.xlsx'
    worksheet_name = '09201_518a2'

    test_data_reference_filename = test_resources / f'{worksheet_name}/data.csv'
    test_metadata_reference_filename = test_resources / f'{worksheet_name}/metadata.txt'

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir.mkdir(parents=True, exist_ok=True)

        with open(cls.test_filename, 'rb') as file:
            cls.input_file = io.BytesIO(file.read())

        cls.test_data_reference = pd.read_csv(cls.test_data_reference_filename)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.temp_dir)

    def setUp(self) -> None:
        self.test_workbook = openpyxl.load_workbook(self.input_file)
        self.test_worksheet = self.test_workbook[self.worksheet_name]

    def test_parseData(self) -> None:
        trial_site_sheet = TrialSiteSheet(self.test_workbook, self.input_file, self.worksheet_name)
        self.assertIsInstance(trial_site_sheet.data, pd.DataFrame)
        self.assertTrue(trial_site_sheet.data.equals(self.test_data_reference))

    def test_parseMetadata(self) -> None:
        trial_site_sheet = TrialSiteSheet(self.test_workbook, self.input_file, self.worksheet_name)
        self.assertIsInstance(trial_site_sheet.metadata, dict)
        self.assertEqual(trial_site_sheet.metadata, {
            'Forstamt': '5622   Mühlhausen',
            'Revier': 'Langula',
            'Versuch': '09201',
            'Parzelle': '01',
            'Teilfläche': '518 a2',
            'Standort': 'Uff-R2',
            'Höhenlage': '426'
        })

    def test_writeData(self) -> None:
        trial_site_sheet = TrialSiteSheet(self.test_workbook, self.input_file, self.worksheet_name)
        trial_site_sheet.write_data(self.temp_dir / 'data.csv')
        self.assertTrue(filecmp.cmp(self.temp_dir / 'data.csv', self.test_data_reference_filename, shallow=False))

    def test_writeMetadata(self) -> None:
        trial_site_sheet = TrialSiteSheet(self.test_workbook, self.input_file, self.worksheet_name)
        trial_site_sheet.write_metadata(self.temp_dir / 'metadata.txt')
        self.assertTrue(
            filecmp.cmp(self.temp_dir / 'metadata.txt', self.test_metadata_reference_filename, shallow=False))


if __name__ == '__main__':
    # unittest.main()
    exit(1)
