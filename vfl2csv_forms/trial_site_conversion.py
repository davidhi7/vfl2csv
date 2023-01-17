import datetime
import re
from pathlib import Path

import pandas as pd

from vfl2csv_base.TrialSite import TrialSite
from vfl2csv_forms import column_scheme
from vfl2csv_forms.excel import styles
from vfl2csv_forms.output.FormulaeColumn import FormulaeColumn
from vfl2csv_forms.output.TrialSiteFormular import TrialSiteFormular

measurement_column_pattern = re.compile(r'\w+_\d{4}')


def convert(trial_site: TrialSite, output_path: Path) -> TrialSiteFormular:
    trial_site.verify_column_integrity(column_scheme)
    df = trial_site.df
    head_column_count = len(column_scheme.head)
    # replace string labels with tuples of year and type of the value for easier computations
    df.columns = TrialSite.expand_column_labels(df.columns)
    # Determine the latest record year. This year's data will be the reference in the
    latest_year = max(map(lambda label: label[0], df.columns[head_column_count:]))
    # find columns that are supposed to be included into the form
    included_head_columns: list[tuple[int, str]] = list()
    included_body_columns: list[tuple[int, str]] = list()
    for column in column_scheme.head:
        if not column.get('form_include', True):
            continue
        included_head_columns.append((-1, column['override_name'],))

    for column in column_scheme.measurements:
        if not column.get('form_include', True):
            continue
        included_body_columns.append((latest_year, column['override_name']))

    # filter the dataframe
    df = filter_df(df, included_head_columns + included_body_columns, len(included_head_columns) + 1)

    # add new columns for each record attribute with the current year
    current_year = datetime.date.today().year
    formulae_columns = insert_new_columns(current_year, df, included_body_columns)
    # set compressed names (type_YYYY)
    df.columns = TrialSite.compress_column_labels(df.columns)

    return TrialSiteFormular(TrialSite(df, trial_site.metadata), output_path, formulae_columns)


def filter_df(df: pd.DataFrame, columns: list[tuple[int, str]], lower_notnull_offset: int) -> pd.DataFrame:
    """
    Filter dataframe:
    1. Filter columns, only select those whose labels are in the `column` parameter
    2. Filter rows that have a greater or equal count of notnull values than `lower_notnull_offset`.
    If `lower_notnull_offset` equals the number of filtered head columns, then any column that contains at least one
    measurement value in the remaining columns is included.
    """
    df = df[columns]
    return df[df.notnull().sum(axis='columns') >= lower_notnull_offset]


def insert_new_columns(df, new_year, column_templates):
    formulae_columns = []
    for column_template in column_templates:
        column_name = column_template[1]
        column_layout = column_scheme.measurements.by_name[column_name]
        # index of the old column in df
        column_index = df.columns.get_loc(column_template)
        # datatype of the old column, will also be the datatype of the new column
        column_datatype = df[column_template].dtype
        # allow for multiple output values, e.g. two diameter measurements
        if column_layout.get('new_columns_count', 1) > 1:
            columns_count = column_layout['new_columns_count']
            # iterate in a declining manner so that the new column with the highest index is shifted the farthest away
            # from the index
            for i in range(columns_count, 0, -1):
                df.insert(column_index + 1, (new_year, f'{column_name}{i}'), pd.Series(dtype=column_datatype))

            # add formula column that calculates the mean of the new column's values
            formula_column = FormulaeColumn(False, 'AVERAGE', f'{column_name}_{new_year}',
                                            list(range(column_index + 1, column_index + 1 + columns_count)),
                                            styles.table_body_rational.name, [])
            formulae_columns.append(formula_column)
            if column_layout.get('add_difference', False):
                formulae_columns.append(
                    FormulaeColumn(True, '-', f'Diff {column_name}', [formula_column, column_index],
                                   styles.table_body_rational.name, styles.full_conditional_formatting_list))
        else:
            df.insert(column_index + 1, (new_year, column_name), pd.Series(dtype=column_datatype))
            if column_layout.get('add_difference', False):
                formulae_columns.append(
                    FormulaeColumn(True, '-', f'Diff {column_name}_{new_year}', [column_index + 1, column_index],
                                   styles.table_body_rational.name, styles.full_conditional_formatting_list))
    return formulae_columns
