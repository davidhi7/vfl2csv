import unittest
from pathlib import Path

import pandas as pd

from TrialSite import TrialSite


class TrialSiteTest(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
