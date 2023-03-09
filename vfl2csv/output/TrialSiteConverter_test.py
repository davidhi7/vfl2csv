import re
import shutil
import unittest
from datetime import date

import pandas as pd
from pandas import MultiIndex

from vfl2csv.output.TrialSiteConverter import TrialSiteConverter
from vfl2csv_base import test_config
from vfl2csv_base.TrialSite import TrialSite


# noinspection PyTypeChecker
class TrialSiteConverterTest(unittest.TestCase):
    tmp_dir = test_config['Output'].getpath('temp_dir')

    sample_multiIndex = MultiIndex.from_tuples([
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

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp_dir)

    def test_refactor_dataframe(self):
        df = pd.DataFrame(columns=self.sample_multiIndex)
        trial_site_converter = TrialSiteConverter(TrialSite(df, metadata=dict()))
        trial_site_converter.refactor_dataframe()
        df = trial_site_converter.trial_site.df
        # expect 2 tree data labels (id and species) and 12 (4*3) measurement columns
        self.assertEqual(len(df.columns), 15)
        self.assertEqual(df.columns[0], 'Bestandeseinheit')
        self.assertEqual(df.columns[1], 'Baumart')
        self.assertEqual(df.columns[2], 'Baumnummer')
        for i, column_label in enumerate(df.columns[3:]):
            self.assertIsInstance(column_label, str)
            if i % 3 == 0:
                # first measurement type: diameter
                self.assertIsNotNone(re.fullmatch(r'D_\d{4}', column_label))
            elif i % 3 == 1:
                # second measurement type: ausscheidungskennung
                self.assertIsNotNone(re.fullmatch(r'Aus_\d{4}', column_label))
            elif i % 3 == 2:
                # third measurement type: height
                self.assertIsNotNone(re.fullmatch(r'H_\d{4}', column_label))
        self.assertEqual(df.dtypes.array, (pd.UInt16Dtype, pd.StringDtype, pd.UInt16Dtype) + 4 * (
            pd.Float64Dtype, pd.UInt8Dtype, pd.Float64Dtype))

    def test_trim_metadata(self):
        trial_site_converter = TrialSiteConverter(TrialSite(df=None, metadata={
            '0': '    ',
            '1': 'a  b',
            '2': 'a\nb',
            '3': 'a \n b'
        }))
        expectations = [' ', 'a b', 'a b', 'a b']
        trial_site_converter.trim_metadata()
        for i in range(4):
            self.assertEqual(trial_site_converter.trial_site.metadata[str(i)], expectations[i])

    def test_refactor_dataframe_exceptions(self):
        # test empty column set
        trial_site = TrialSiteConverter(TrialSite(pd.DataFrame(columns=MultiIndex.from_tuples([()])), metadata=dict()))
        self.assertRaises(ValueError, trial_site.refactor_dataframe)

        # test column set with fewer columns than head columns in the template
        trial_site = TrialSiteConverter(TrialSite(pd.DataFrame(columns=MultiIndex.from_tuples([
            ('Aufnahme', 'Wert', 'Einheit', 'Bst.-E.'),
            ('Aufnahme', 'Wert', 'Einheit', 'Art')
        ])), metadata=dict()))
        self.assertRaises(ValueError, trial_site.refactor_dataframe)

        # test column set with measurement columns lacking one field compared to the template
        trial_site = TrialSiteConverter(TrialSite(pd.DataFrame(columns=MultiIndex.from_tuples([
            ('Aufnahme', 'Wert', 'Einheit', 'Bst.-E.'),
            ('Aufnahme', 'Wert', 'Einheit', 'Art'),
            ('Aufnahme', 'Wert', 'Einheit', 'Baum'),
            ('23.07.1984', 'D', 'cm', '159'),
            ('23.07.1984', 'Aus', 'Unnamed: 4_level_2', '15')
        ])), metadata=dict()))
        self.assertRaises(ValueError, trial_site.refactor_dataframe)

    def test_simplifyColumnLabels_expect_decremented_year(self) -> None:
        self.assertEqual('D_2021', TrialSiteConverter.simplify_measurement_column_labels(
            (date.fromisoformat('2022-01-01'), 'D', 'cm', '0'), override_name=None))
        self.assertEqual('H_2021', TrialSiteConverter.simplify_measurement_column_labels(
            (date.fromisoformat('2022-05-31'), 'H', 'm', '0'),
            override_name=None)
                         )

        self.assertEqual('test123_2021', TrialSiteConverter.simplify_measurement_column_labels(
            (date.fromisoformat('2022-01-01'), 'D', 'cm', '0'), override_name='test123'))
        self.assertEqual('test456_2021', TrialSiteConverter.simplify_measurement_column_labels(
            (date.fromisoformat('2022-05-31'), 'H', 'm', '0'),
            override_name='test456')
                         )

    def test_simplifyColumnLabels_expect_equal_year(self) -> None:
        self.assertEqual('D_2022', TrialSiteConverter.simplify_measurement_column_labels(
            (date.fromisoformat('2022-06-01'), 'D', 'cm', '0'), override_name=None))
        self.assertEqual('H_2022', TrialSiteConverter.simplify_measurement_column_labels(
            (date.fromisoformat('2022-12-31'), 'H', 'm', '0'),
            override_name=None)
                         )

        self.assertEqual('test123_2022', TrialSiteConverter.simplify_measurement_column_labels(
            (date.fromisoformat('2022-06-01'), 'D', 'cm', '0'), override_name='test123'))
        self.assertEqual('test456_2022', TrialSiteConverter.simplify_measurement_column_labels(
            (date.fromisoformat('2022-12-31'), 'H', 'm', '0'),
            override_name='test456')
                         )

    def test_writeData(self):
        test_df = pd.DataFrame.from_dict({
            'meta-data': [
                1, 2, 3
            ],
            'D_2014': [
                pd.NA, pd.NA, pd.NA
            ]
        })
        trial_site = TrialSiteConverter(TrialSite(df=test_df, metadata=dict()))
        trial_site.write_data(filepath=self.tmp_dir / 'data.csv')
        with open(self.tmp_dir / 'data.csv', 'r') as file:
            self.assertEqual(file.read(), "meta-data,D_2014\n1,NA\n2,NA\n3,NA\n")

    def test_writeMetadata(self):
        test_metadata = {
            'key-1': 'value-1',
            'key-2': 'value-2',
            'key-3': 'value-3'
        }
        trial_site = TrialSiteConverter(TrialSite(df=pd.DataFrame(), metadata=test_metadata))
        trial_site.write_metadata(filepath=self.tmp_dir / 'metadata.txt')
        with open(self.tmp_dir / 'metadata.txt', 'r') as file:
            self.assertEqual(file.read(), "key-1=value-1\nkey-2=value-2\nkey-3=value-3\n")


if __name__ == '__main__':
    unittest.main()
