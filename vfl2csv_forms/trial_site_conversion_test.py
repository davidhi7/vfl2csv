import unittest

import pandas as pd

from vfl2csv_forms.trial_site_conversion import filter_df


class TrialSiteConversionTest(unittest.TestCase):
    def test_filter_rows(self):
        df = pd.DataFrame(
            {
                (-1, "head1"): ["test1", "test2", "test3"],
                (-1, "head2"): ["test1", "test2", "test3"],
                (2000, "measurement"): [1, 1, 1],
                (2005, "measurement"): [1, 1, pd.NA],
                (2010, "measurement"): [1, pd.NA, pd.NA],
                (2015, "measurement"): [pd.NA, pd.NA, pd.NA],
            }
        )
        result1 = filter_df(
            df.copy(deep=True),
            [
                (-1, "head1"),
                (-1, "head2"),
                (2000, "measurement"),
                (2005, "measurement"),
                (2010, "measurement"),
                (2015, "measurement"),
            ],
            2,
        )
        self.assertEqual(len(result1.index), 3)

        result2 = filter_df(
            df.copy(deep=True),
            [
                (-1, "head1"),
                (-1, "head2"),
                (2000, "measurement"),
                (2005, "measurement"),
                (2010, "measurement"),
                (2015, "measurement"),
            ],
            3,
        )
        self.assertEqual(len(result2.index), 3)

        result3 = filter_df(
            df.copy(deep=True),
            [
                (-1, "head1"),
                (-1, "head2"),
                (2000, "measurement"),
                (2005, "measurement"),
                (2010, "measurement"),
                (2015, "measurement"),
            ],
            5,
        )
        self.assertEqual(len(result3.index), 1)
        self.assertEqual(result3[(-1, "head1")][0], "test1")

        result4 = filter_df(
            df.copy(deep=True),
            [
                (-1, "head1"),
                (-1, "head2"),
                (2000, "measurement"),
                (2005, "measurement"),
                (2010, "measurement"),
                (2015, "measurement"),
            ],
            6,
        )
        self.assertEqual(len(result4.index), 0)

    def test_filter_columns(self):
        df = pd.DataFrame(
            {
                (-1, "head1"): ["test1", "test2", "test3"],
                (-1, "head2"): ["test1", "test2", "test3"],
                (2000, "measurement"): [1, 1, 1],
                (2005, "measurement"): [1, 1, pd.NA],
                (2010, "measurement"): [1, pd.NA, pd.NA],
                (2015, "measurement"): [pd.NA, pd.NA, pd.NA],
            }
        )
        # high `lower_notnull_offset` since this parameter should not affect the columns of the returned dataframe
        self.assertEqual(
            filter_df(
                df,
                [
                    (-1, "head1"),
                    (-1, "head2"),
                    (2000, "measurement"),
                    (2010, "measurement"),
                ],
                100,
            ).columns.values.tolist(),
            [
                (-1, "head1"),
                (-1, "head2"),
                (2000, "measurement"),
                (2010, "measurement"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
