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
    head_columns: list[tuple[int, str]] = list()
    body_columns: list[tuple[int, str]] = list()
    for column in column_scheme.head:
        if not column.get('form_include', True):
            continue
        head_columns.append((-1, column['override_name'],))

    for column in column_scheme.measurements:
        if not column.get('form_include', True):
            continue
        body_columns.append((latest_year, column['override_name']))
    # create a subset of df containing only relevant columns
    df_subset = df[head_columns + body_columns]
    # filter out all rows that have no value in any record attribute
    df_subset = df_subset[df_subset.notnull().sum(axis='columns') > head_column_count]
    # add new columns for each record attribute with the current year
    current_year = datetime.date.today().year
    formulae_columns: list[FormulaeColumn] = []
    for column in body_columns:
        column_name = column[1]
        layout = column_scheme.measurements.by_name[column_name]
        index = df_subset.columns.get_loc(column)
        # datatype of this column and all associated columns
        column_datatype = df[column].dtype
        # allow for multiple output values, e.g. two diameter measurements
        if layout.get('new_columns_count', 1) > 1:
            columns_count = layout['new_columns_count']
            formulae_column = FormulaeColumn(False, 'AVERAGE', f'{column_name}_{current_year}',
                                             list(range(index + 1, index + 1 + columns_count)),
                                             styles.table_body_rational.name, [])
            formulae_columns.append(formulae_column)
            # iterate in a declining manner so that the column with the highest index is shifted the farthest away
            # from the index
            for i in range(layout['new_columns_count'], 0, -1):
                df_subset.insert(index + 1, (current_year, f'{column_name}{i}'), pd.Series(dtype=column_datatype))
            if layout.get('add_difference', False):
                formulae_columns.append(
                    FormulaeColumn(True, '-', f'Diff {column_name}', [formulae_column, index],
                                   styles.table_body_rational.name, [styles.conditional_formatting_less_than,
                                                                     styles.conditional_formatting_greater_than]))
        else:
            df_subset.insert(index + 1, (current_year, column_name), pd.Series(dtype=column_datatype))
            if layout.get('add_difference', False):
                formulae_columns.append(
                    FormulaeColumn(True, '-', f'Diff {column_name}_{current_year}', [index + 1, index],
                                   styles.table_body_rational.name, [styles.conditional_formatting_less_than,
                                                                     styles.conditional_formatting_greater_than]))
    # set compressed names (type_YYYY)
    df_subset.columns = TrialSite.compress_column_labels(df_subset.columns)
    return TrialSiteFormular(TrialSite(df_subset, trial_site.metadata), output_path, formulae_columns)
