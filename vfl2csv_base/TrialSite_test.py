import unittest
from pathlib import Path

import pandas as pd

from vfl2csv_base import test_config
from vfl2csv_base.ColumnScheme import ColumnScheme
from vfl2csv_base.TrialSite import TrialSite, ExpandedColumnNotation
from vfl2csv_base.exceptions.IOErrors import TrialSiteFormatError


class TrialSiteTest(unittest.TestCase):
    sample_metadata = {
        "Forstamt": "5628   Bad Berka",
        "Revier": "Tiefborn",
        "Versuch": "09703",
        "Parzelle": "02",
        "Teilfläche": "2524 a3",
        "Standort": "Uf-K1",
        "Höhenlage": "420",
    }

    sample_head_scheme = [
        {"name": "Bst.-E.", "override_name": "Bestandeseinheit", "type": "uint16"},
        {"name": "Art", "override_name": "Baumart", "type": "string"},
        {"name": "Baum", "override_name": "Baumnummer", "type": "uint32"},
    ]

    sample_measurements_scheme = [
        {"name": "D", "type": "float64"},
        {"name": "Aus", "type": "uint16"},
    ]

    pattern_string_1 = (
        "{forstamt}:{revier}:{versuch}:{parzelle}:{teilfläche}:{standort}:{höhenlage}"
    )
    pattern_string_2 = (
        "{forstamt}:{forstamt}:{forstamt}:{teilfläche}:{teilfläche}:{teilfläche}"
    )
    expected_matched_string_1 = "5628   Bad Berka:Tiefborn:09703:02:2524 a3:Uf-K1:420"
    expected_matched_string_2 = (
        "5628   Bad Berka:5628   Bad Berka:5628   Bad Berka:2524 a3:2524 a3:2524 a3"
    )

    def test_replaceMetadataKeys_strings(self) -> None:
        trial_site = TrialSite(pd.DataFrame(), self.sample_metadata)
        self.assertEqual(
            trial_site.replace_metadata_keys(self.pattern_string_1),
            self.expected_matched_string_1,
        )
        self.assertEqual(
            trial_site.replace_metadata_keys(self.pattern_string_2),
            self.expected_matched_string_2,
        )

    def test_replaceMetadataKeys_paths(self) -> None:
        trial_site = TrialSite(pd.DataFrame(), self.sample_metadata)

        self.assertEqual(
            trial_site.replace_metadata_keys(Path(self.pattern_string_1)),
            Path(self.expected_matched_string_1),
        )
        self.assertEqual(
            trial_site.replace_metadata_keys(Path(self.pattern_string_2)),
            Path(self.expected_matched_string_2),
        )

    def test_verifyIntegrity_head(self) -> None:
        column_scheme = ColumnScheme(
            head=self.sample_head_scheme, measurements=self.sample_measurements_scheme
        )
        trial_site = TrialSite(
            df=pd.DataFrame(columns=["Bestandeseinheit", "Baumart", "Baumnummer"]),
            metadata={},
        )
        trial_site.verify_column_integrity(column_scheme)
        self.assertEqual(
            trial_site.df.dtypes.values.tolist(),
            [pd.UInt16Dtype(), pd.StringDtype(), pd.UInt32Dtype()],
        )

    def test_verifyIntegrity_measurements(self) -> None:
        column_scheme = ColumnScheme(
            head=[], measurements=self.sample_measurements_scheme
        )
        trial_site = TrialSite(
            df=pd.DataFrame(
                columns=[
                    "D_1980",
                    "Aus_1980",
                    "D_2000",
                    "Aus_2000",
                    "D_2020",
                    "Aus_2020",
                ]
            ),
            metadata={},
        )
        trial_site.verify_column_integrity(column_scheme)
        self.assertEqual(
            trial_site.df.dtypes.values.tolist(),
            3 * [pd.Float64Dtype(), pd.UInt16Dtype()],
        )

    def test_verifyIntegrity_combined(self) -> None:
        column_scheme = ColumnScheme(
            head=self.sample_head_scheme, measurements=self.sample_measurements_scheme
        )
        trial_site = TrialSite(
            df=pd.DataFrame(
                columns=[
                    "Bestandeseinheit",
                    "Baumart",
                    "Baumnummer",
                    "D_1980",
                    "Aus_1980",
                    "D_2000",
                    "Aus_2000",
                    "D_2020",
                    "Aus_2020",
                ]
            ),
            metadata={},
        )
        trial_site.verify_column_integrity(column_scheme)
        self.assertEqual(
            trial_site.df.dtypes.values.tolist(),
            [pd.UInt16Dtype(), pd.StringDtype(), pd.UInt32Dtype()]
            + 3 * [pd.Float64Dtype(), pd.UInt16Dtype()],
        )

    def test_verifyIntegrity_head_errors(self) -> None:
        column_scheme = ColumnScheme(
            head=self.sample_head_scheme, measurements=self.sample_measurements_scheme
        )
        trial_site = TrialSite(
            df=pd.DataFrame(columns=["Bestandeseinheit_typo", "Baumart", "Baumnummer"]),
            metadata={},
        )
        self.assertRaises(
            TrialSiteFormatError, trial_site.verify_column_integrity, column_scheme
        )

    def test_verifyIntegrity_measurements_errors(self) -> None:
        column_scheme = ColumnScheme(
            head=self.sample_head_scheme, measurements=self.sample_measurements_scheme
        )
        trial_site = TrialSite(
            df=pd.DataFrame(
                columns=[
                    "D_typo_1980",
                    "Aus_1980",
                    "D_2000",
                    "Aus_2000",
                    "D_2020",
                    "Aus_2020",
                ]
            ),
            metadata={},
        )
        self.assertRaises(
            TrialSiteFormatError, trial_site.verify_column_integrity, column_scheme
        )

    def test_verifyIntegrity_head_errors_missing(self) -> None:
        column_scheme = ColumnScheme(
            head=self.sample_head_scheme, measurements=self.sample_measurements_scheme
        )
        trial_site = TrialSite(
            df=pd.DataFrame(columns=["Baumart", "Baumnummer"]), metadata={}
        )
        self.assertRaises(
            TrialSiteFormatError, trial_site.verify_column_integrity, column_scheme
        )

    def test_verifyIntegrity_measurements_errors_missing(self) -> None:
        column_scheme = ColumnScheme(
            head=[], measurements=self.sample_measurements_scheme
        )
        trial_site = TrialSite(
            df=pd.DataFrame(
                columns=["Aus_1980", "D_2000", "Aus_2000", "D_2020", "Aus_2020"]
            ),
            metadata={},
        )
        self.assertRaises(
            TrialSiteFormatError, trial_site.verify_column_integrity, column_scheme
        )

    def test_expandColumnLabels(self):
        self.assertEqual(
            list(
                TrialSite.expand_column_labels(
                    ["Baumart", "Baumnummer", "D_2000", "Aus_2000"]
                )
            ),
            [(-1, "Baumart"), (-1, "Baumnummer"), (2000, "D"), (2000, "Aus")],
        )

    def test_compressColumnLabels(self):
        self.assertEqual(
            list(
                TrialSite.compress_column_labels(
                    [
                        ExpandedColumnNotation(-1, "Baumart"),
                        ExpandedColumnNotation(-1, "Baumnummer"),
                        ExpandedColumnNotation(2000, "D"),
                        ExpandedColumnNotation(2000, "Aus"),
                    ]
                )
            ),
            ["Baumart", "Baumnummer", "D_2000", "Aus_2000"],
        )

    def test_fromMetaDataFile(self) -> None:
        trial_site = TrialSite.from_metadata_file(
            Path(test_config["Input"]["metadata_sample_output_file"])
        )
        expected_df = pd.read_csv(test_config["Input"]["csv_sample_output_file"])
        self.assertTrue(trial_site.df.equals(expected_df))
        self.assertDictEqual(
            trial_site.metadata,
            {
                "Forstamt": "44 Schönheide",
                "Revier": "Hundshübel",
                "Versuch": "14607",
                "Parzelle": "01",
                "Teilfläche": "112 a2",
                "Standort": "Mf-Z3",
                "Höhenlage": "680",
                "DataFrame": "14607-01.csv",
            },
        )

    def test_verifyIntegrity_optional_columns(self):
        measurements_column_scheme = list(self.sample_measurements_scheme)
        measurements_column_scheme.append(
            {
                "name": "Typ-D",
                # "optional": True,
                "type": "uint16",
            }
        )
        column_scheme = ColumnScheme(head=[], measurements=measurements_column_scheme)
        trial_site = TrialSite(
            df=pd.DataFrame(
                columns=["D_2000", "Aus_2000", "Typ-D_2000", "D_2010", "Aus_2010"]
            ),
            metadata={},
        )
        # Expect error because `Typ-D` is not optional
        self.assertRaises(
            TrialSiteFormatError, trial_site.verify_column_integrity, column_scheme
        )
        # measurements_column_scheme[-1]['optional'] = True
        column_scheme.measurements.by_name["Typ-D"]["optional"] = True
        # Do no longer expect error as column is optional now
        trial_site.verify_column_integrity(column_scheme)


if __name__ == "__main__":
    unittest.main()
