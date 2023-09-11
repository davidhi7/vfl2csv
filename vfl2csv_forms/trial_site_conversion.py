import datetime
import re
from pathlib import Path

import pandas as pd

import vfl2csv_forms
from vfl2csv_base.TrialSite import TrialSite, ExpandedColumnNotation
from vfl2csv_forms.excel import styles
from vfl2csv_forms.excel.FormulaColumn import FormulaColumn
from vfl2csv_forms.excel.TrialSiteForm import TrialSiteForm

measurement_column_pattern = re.compile(r"\w+_\d{4}")


def convert(trial_site: TrialSite, output_path: Path) -> TrialSiteForm:
    trial_site.verify_column_integrity(vfl2csv_forms.column_scheme)
    df, metadata = trial_site.df.copy(), trial_site.metadata
    # replace string labels with tuples of year and type of the value for easier computations
    df.columns = list(TrialSite.expand_column_labels(df.columns))

    # Determine the latest measurement year. Its data will act as the reference in the formular
    latest_year = max(
        map(lambda label: label[0], df.columns[len(vfl2csv_forms.column_scheme.head):])
    )

    # find columns that are supposed to be included into the form
    # namely, all head columns and all measurement columns of `last_year`, both unless explicitly disabled in the
    # column scheme
    included_head_columns: list[ExpandedColumnNotation] = list()
    included_body_columns: list[ExpandedColumnNotation] = list()
    for column in vfl2csv_forms.column_scheme.head:
        if not column.get("form_include", True):
            continue
        column_name = column.get("override_name", column["name"])
        # allow to manually set the display name for the form
        if "display_name" in column:
            display_name = column.get("display_name")
            df = df.rename(
                columns={
                    (-1, column_name): (
                        ExpandedColumnNotation(year=-1, name=display_name)
                    )
                }
            )
            column_name = display_name
        included_head_columns.append(ExpandedColumnNotation(year=-1, name=column_name))
    for column in vfl2csv_forms.column_scheme.measurements:
        if not column.get("form_include", True):
            continue
        included_body_columns.append(
            ExpandedColumnNotation(
                year=latest_year, name=column.get("override_name", column["name"])
            )
        )

    # filter the dataframe: filter out unneeded rows and columns
    df = filter_df(
        df,
        columns=included_head_columns + included_body_columns,
        lower_notnull_offset=len(included_head_columns) + 1,
    )

    # add new columns for each record attribute with the current year
    df, formulae_columns = insert_new_columns(
        df, datetime.date.today().year, included_body_columns
    )

    # apply `display_name` values for old columns, must happen after insert_new_columns
    for column in included_body_columns:
        template = vfl2csv_forms.column_scheme.measurements.by_name[column[1]]
        if "display_name" in template:
            df = df.rename(columns={column: (column[0], template["display_name"])})

    # set compressed column names again (type_YYYY)
    df.columns = list(TrialSite.compress_column_labels(df.columns))
    return TrialSiteForm(TrialSite(df, metadata), output_path, formulae_columns)


def filter_df(
        df: pd.DataFrame, columns: list[ExpandedColumnNotation], lower_notnull_offset: int
) -> pd.DataFrame:
    """
    Filter dataframe:
    1. Filter columns, only select those whose labels are in the `column` parameter
    2. Filter rows that have a greater or equal count of notnull values than `lower_notnull_offset`.
    If `lower_notnull_offset` equals the number of filtered head columns, then any column that contains at least one
    measurement value in the remaining columns is included.
    """
    df = df.filter(columns)
    return df[df.notnull().sum(axis="columns") >= lower_notnull_offset]


def insert_new_columns(
        df: pd.DataFrame, new_year: int, old_columns: list[ExpandedColumnNotation]
) -> tuple[pd.DataFrame, list[FormulaColumn]]:
    formula_columns = []
    for old_column in old_columns:
        column_name = old_column[1]
        template = vfl2csv_forms.column_scheme.measurements.by_name[column_name]
        column_name = template.get("display_name", column_name)
        # index of the old column in df
        column_index = df.columns.get_loc(old_column)
        # datatype of the old column, will also be the datatype of the new column
        column_datatype = df[old_column].dtype
        # allow for multiple output values, e.g. two diameter measurements
        if template.get("new_columns_count", 1) > 1:
            columns_count = template["new_columns_count"]
            # iterate in a declining manner so that the new column with the highest index is shifted the farthest away
            # from the index
            for i in range(columns_count, 0, -1):
                df.insert(
                    column_index + 1,
                    (new_year, f"{column_name}{i}"),
                    pd.Series(dtype=column_datatype),
                )

            # add formula column that calculates the mean of the new column's values
            formula_column = FormulaColumn(
                False,
                "AVERAGE",
                f"{column_name}_{new_year}",
                list(range(column_index + 1, column_index + 1 + columns_count)),
                styles.table_body_rational,
                [],
            )
            formula_columns.append(formula_column)
            if template.get("add_difference", False):
                formula_columns.append(
                    FormulaColumn(
                        True,
                        "-",
                        f"Diff {column_name}",
                        [formula_column, column_index],
                        styles.table_body_rational,
                        styles.full_conditional_formatting_list(),
                    )
                )
        else:
            df.insert(
                column_index + 1,
                (new_year, column_name),
                pd.Series(dtype=column_datatype),
            )
            if template.get("add_difference", False):
                formula_columns.append(
                    FormulaColumn(
                        True,
                        "-",
                        f"Diff {column_name}",
                        [column_index + 1, column_index],
                        styles.table_body_rational,
                        styles.full_conditional_formatting_list(),
                    )
                )
    return df, formula_columns
