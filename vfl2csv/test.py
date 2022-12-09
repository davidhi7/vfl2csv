import datetime
import filecmp
import io
import shutil
import unittest
from pathlib import Path

import openpyxl
import pandas as pd

from TrialSiteSheet import TrialSiteSheet


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

    def test_simplifyColumnLabels_expect_decremented_year(self) -> None:
        self.assertEqual('D_2021', TrialSiteSheet.simplify_column_labels(
                             (datetime.date.fromisoformat('2022-01-01'), 'D', 'cm', '0')
        ))
        self.assertEqual('H_2021', TrialSiteSheet.simplify_column_labels(
            (datetime.date.fromisoformat('2022-05-31'), 'H', 'm', '0')
        ))

    def test_simplifyColumnLabels_expect_equal_year(self) -> None:
        self.assertEqual('D_2022', TrialSiteSheet.simplify_column_labels(
                             (datetime.date.fromisoformat('2022-06-01'), 'D', 'cm', '0')
        ))
        self.assertEqual('H_2022', TrialSiteSheet.simplify_column_labels(
            (datetime.date.fromisoformat('2022-12-31'), 'H', 'm', '0')
        ))

    def test_replaceMetadataKeys(self) -> None:
        trial_site_sheet = TrialSiteSheet(self.test_workbook, self.input_file, self.worksheet_name)
        self.assertEqual('5622   Mühlhausen:Langula:09201:01:518 a2:Uff-R2:426', trial_site_sheet.replace_metadata_keys('{forstamt}:{revier}:{versuch}:{parzelle}:{teilfläche}:{standort}:{höhenlage}'))
        self.assertEqual('5622   Mühlhausen:5622   Mühlhausen:5622   Mühlhausen:518 a2:518 a2:518 a2', trial_site_sheet.replace_metadata_keys('{forstamt}:{forstamt}:{forstamt}:{teilfläche}:{teilfläche}:{teilfläche}'))


if __name__ == '__main__':
    unittest.main()
