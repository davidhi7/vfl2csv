import re
import shutil
import unittest
from datetime import date
from pathlib import Path

import pandas as pd
from pandas import MultiIndex

from output.TrialSiteConverter import TrialSite
from test.testconfig import config


class TrialSiteConverterTest(unittest.TestCase):
    sample_metadata = {
        "Forstamt": "5628   Bad Berka",
        "Revier": "Tiefborn",
        "Versuch": "09703",
        "Parzelle": "02",
        "Teilfläche": "2524 a3",
        "Standort": "Uf-K1",
        "Höhenlage": "420"
    }
    pattern_string_1 = '{forstamt}:{revier}:{versuch}:{parzelle}:{teilfläche}:{standort}:{höhenlage}'
    pattern_string_2 = '{forstamt}:{forstamt}:{forstamt}:{teilfläche}:{teilfläche}:{teilfläche}'
    expected_matched_string_1 = '5628   Bad Berka:Tiefborn:09703:02:2524 a3:Uf-K1:420'
    expected_matched_string_2 = '5628   Bad Berka:5628   Bad Berka:5628   Bad Berka:2524 a3:2524 a3:2524 a3'

    tmp_dir = config['Output'].getpath('temp_dir')

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp_dir)

    def test_refactor_dataframe(self):
        multiIndex = MultiIndex.from_tuples([
            ('Aufnahme', 'Wert', 'Einheit', 'Bst.-E.'),
            ('Aufnahme', 'Wert', 'Einheit', 'Art'),
            ('Aufnahme', 'Wert', 'Einheit', 'Baum'),
            ('23.07.1984', 'D', 'cm', '159'),
            ('23.07.1984', 'Aus', 'Unnamed: 4_level_2', '15'),
            ('23.07.1984', 'H', 'm', '30'),
            ('26.04.1995', 'D', 'cm', '144'),
            ('26.04.1995', 'Aus', 'Unnamed: 7_level_2', '50'),
            ('26.04.1995', 'H', 'm', '34'),
            ('10.11.2006', 'D', 'cm', '94'),
            ('10.11.2006', 'Aus', 'Unnamed: 10_level_2', '31'),
            ('10.11.2006', 'H', 'm', '30'),
            ('03.12.2013', 'D', 'cm', '63'),
            ('03.12.2013', 'Aus', 'Unnamed: 13_level_2', '0'),
            ('03.12.2013', 'H', 'm', '33')
        ])
        df = pd.DataFrame(columns=multiIndex)
        trial_site = TrialSite(df, metadata=dict())
        trial_site.refactor_dataframe()
        df = trial_site.df
        # expect 2 tree data labels (id and species) and 12 (4*3) measurement columns
        self.assertEqual(len(df.columns), 14)
        self.assertEqual(df.columns[0], 'Baumart')
        self.assertEqual(df.columns[1], 'Baumnummer')
        for i, column_label in enumerate(df.columns[2:]):
            self.assertIsInstance(column_label, str)
            if (i + 3) % 3 == 0:
                # first measurement type: diameter
                self.assertIsNotNone(re.fullmatch(r'D_\d{4}', column_label))
            elif (i + 3) % 3 == 1:
                # second measurement type: ausscheidungskennung
                self.assertIsNotNone(re.fullmatch(r'Aus_\d{4}', column_label))
            elif (i + 3) % 3 == 2:
                # third measurement type: height
                self.assertIsNotNone(re.fullmatch(r'H_\d{4}', column_label))

    def test_simplifyColumnLabels_expect_decremented_year(self) -> None:
        self.assertEqual('D_2021', TrialSite.simplify_column_labels((date.fromisoformat('2022-01-01'), 'D', 'cm', '0')))
        self.assertEqual('H_2021', TrialSite.simplify_column_labels((date.fromisoformat('2022-05-31'), 'H', 'm', '0')))

    def test_simplifyColumnLabels_expect_equal_year(self) -> None:
        self.assertEqual('D_2022', TrialSite.simplify_column_labels((date.fromisoformat('2022-06-01'), 'D', 'cm', '0')))
        self.assertEqual('H_2022', TrialSite.simplify_column_labels((date.fromisoformat('2022-12-31'), 'H', 'm', '0')))

    def test_replaceMetadataKeys_strings(self) -> None:
        trial_site = TrialSite(pd.DataFrame(), self.sample_metadata)
        self.assertEqual(trial_site.replace_metadata_keys(self.pattern_string_1), self.expected_matched_string_1)
        self.assertEqual(trial_site.replace_metadata_keys(self.pattern_string_2), self.expected_matched_string_2)

    def test_replaceMetadataKeys_paths(self) -> None:
        trial_site = TrialSite(pd.DataFrame(), self.sample_metadata)

        self.assertEqual(trial_site.replace_metadata_keys(Path(self.pattern_string_1)),
                         Path(self.expected_matched_string_1))
        self.assertEqual(trial_site.replace_metadata_keys(Path(self.pattern_string_2)),
                         Path(self.expected_matched_string_2))

    def test_writeData(self):
        test_df = pd.DataFrame.from_dict({
            'meta-data': [
                1, 2, 3
            ],
            'D_2014': [
                pd.NA, pd.NA, pd.NA
            ]
        })
        trial_site = TrialSite(df=test_df, metadata=dict())
        trial_site.write_data(filepath=self.tmp_dir / 'data.csv')
        with open(self.tmp_dir / 'data.csv', 'r') as file:
            self.assertEqual(file.read(), "meta-data,D_2014\n1,NA\n2,NA\n3,NA\n")

    def test_writeMetadata(self):
        test_metadata = {
            'key-1': 'value-1',
            'key-2': 'value-2',
            'key-3': 'value-3'
        }
        trial_site = TrialSite(df=pd.DataFrame(), metadata=test_metadata)
        trial_site.write_metadata(filepath=self.tmp_dir / 'metadata.txt')
        with open(self.tmp_dir / 'metadata.txt', 'r') as file:
            self.assertEqual(file.read(), "key-1=value-1\nkey-2=value-2\nkey-3=value-3\n")


if __name__ == '__main__':
    unittest.main()
