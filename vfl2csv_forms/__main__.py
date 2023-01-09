import datetime
import math
import re
import sys
from pathlib import Path
from typing import Iterator, Generator

import pandas as pd

from excel import styles
from output.FormulaeColumn import FormulaeColumn
from output.TrialSiteFormular import TrialSiteFormular
from vfl2csv_base.input.ColumnLayout import ColumnLayout
from vfl2csv_base.input.TrialSite import TrialSite
from vfl2csv_base.input.datatypes_mapping import pandas_datatypes_mapping as dtypes_mapping

measurement_column_pattern = re.compile(r'\w+_\d{4}')


def compress_column_labels(multiindex: Iterator[tuple[any, str]]) -> Generator[str, None, None]:
    """
    Convert labels from the tuple `(year, type)` (`(type)` for tree metadata labels) into the string 'type_year'
    """
    for label in multiindex:
        if label[0] > 0:
            yield f'{label[1]}_{label[0]}'
        else:
            yield label[1]


def expand_column_labels(index: Iterator[str]) -> Generator[tuple[str], None, None]:
    """
    Convert labels from the string 'type_year' into the tuple `(year, type)` (`(type)` for tree metadata labels)
    """

    for label in index:
        if measurement_column_pattern.fullmatch(label):
            record_type, record_year = label.split('_')
            yield int(record_year), record_type
        else:
            # for head columns, only use the original column label
            yield math.nan, label


def parse_metadata(path: Path) -> dict[str, str]:
    metadata = dict()
    with open(path, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            # use maxsplit to avoid removing equality symbols in the value
            key, value = line.split('=', maxsplit=1)
            # remove trailing newline in value
            metadata[key] = value.rstrip()
    return metadata


if __name__ == '__main__':
    #### READ INPUT ####
    # config file that contains column information
    column_layout = ColumnLayout(Path('config/columns.json'))

    # parse output file
    input_metadata_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    trial_site = TrialSite.from_metadata_file(input_metadata_file)
    df = trial_site.df

    # counts of head/tree metadata columns
    head_column_count = len(column_layout.head)
    # count of columns per record
    measurements_type_count = len(column_layout.measurements)

    #### start transforming dataframe ####

    # create a new index to work with: first value in multi index is the record year, second value is the measurement
    # value
    df.columns = expand_column_labels(df.columns)

    dtypes_styles_mapping = {
        pd.StringDtype(): styles.table_body_text,
        pd.Int8Dtype(): styles.table_body_integer,
        pd.Int16Dtype(): styles.table_body_integer,
        pd.Int32Dtype(): styles.table_body_integer,
        pd.Int64Dtype(): styles.table_body_integer,
        pd.UInt8Dtype(): styles.table_body_integer,
        pd.UInt16Dtype(): styles.table_body_integer,
        pd.UInt32Dtype(): styles.table_body_integer,
        pd.UInt64Dtype(): styles.table_body_integer,
        pd.Float32Dtype(): styles.table_body_rational,
        pd.Float64Dtype(): styles.table_body_rational
    }

    #### verify trial site, set datatypes ####

    # verify dataframe columns and set datatypes
    for i, column in enumerate(df.columns[:head_column_count]):
        if column[1] != column_layout.head[i]['override_name']:
            raise ValueError(f'Column {column[0]} of the input CSV file does not match the expected name provided in '
                             f'the columns.json file!')
        df[column] = df[column].astype(dtypes_mapping[column_layout.head[i]['type']])

    # count of expected individual records with n columns each
    measurement_count = (len(df.columns) - head_column_count) // measurements_type_count
    for measurement_index in range(measurement_count):
        for attribute_index in range(measurements_type_count):
            column_index = head_column_count + measurement_index * measurements_type_count + attribute_index
            column = df.columns[column_index]
            if column[1] != column_layout.measurements[attribute_index]['override_name']:
                raise ValueError(f'Column {column[1]}_{column[0]} of the input CSV file does not match the expected '
                                 f'name provided in the columns.json file!')
            df[column] = df[column].astype(dtypes_mapping[column_layout.measurements[attribute_index]['type']])

    #### create dataframe subset, filter rows & cols ####

    # Determine the latest record year. This year's data will be the reference in the 
    latest_year = max(map(lambda label: label[0], df.columns[head_column_count:]))

    # find columns that are supposed to be included into the form
    head_columns: list[tuple[int, str]] = list()
    body_columns: list[tuple[int, str]] = list()
    for column in column_layout.head:
        if 'form_include' in column and column['form_include'] is False:
            continue
        head_columns.append((math.nan, column['override_name'],))

    for column in column_layout.measurements:
        if 'form_include' in column and column['form_include'] is False:
            continue
        body_columns.append((latest_year, column['override_name']))

    # create a subset of df containing only relevant columns
    df_subset = df[head_columns + body_columns]
    # filter out all rows that have no value in any record attribute
    df_subset = df_subset[df_subset.notnull().sum(axis='columns') > head_column_count]

    #### add new columns ####

    # add new columns for each record attribute with the current year
    current_year = datetime.date.today().year
    formulae_columns: list[FormulaeColumn] = []
    for column in body_columns:
        column_name = column[1]
        layout = column_layout.measurements.by_name[column_name]
        index = df_subset.columns.get_loc(column)
        # datatype of this column and all associated columns
        column_datatype = df[column].dtype
        # allow for multiple output values, e.g. two diameter measurements
        if layout.get('new_columns_count', 1) > 1:
            columns_count = layout['new_columns_count']
            formulae_column = FormulaeColumn(False, 'AVERAGE', f'{column_name}_{current_year}',
                                             list(range(index + 1, index + 1 + columns_count)),
                                             styles.table_body_rational, [])
            formulae_columns.append(formulae_column)
            # iterate in a declining manner so that the column with the highest index is shifted the farthest away
            # from the index
            for i in range(layout['new_columns_count'], 0, -1):
                df_subset.insert(index + 1, (current_year, f'{column_name}{i}'), pd.Series(data=pd.NA,
                                                                                           dtype=column_datatype))
            if layout.get('add_difference', False):
                formulae_columns.append(
                    FormulaeColumn(True, '-', f'Diff', [formulae_column, index],
                                   styles.table_body_rational, [styles.conditional_formatting_less_than,
                                                                styles.conditional_formatting_greater_than]))
        else:
            df_subset.insert(index + 1, (current_year, column_name), pd.Series(data=pd.NA, dtype=column_datatype))
            if layout.get('add_difference', False):
                formulae_columns.append(
                    FormulaeColumn(True, '-', f'Diff {column_name}_{current_year}', [index + 1, index],
                                   styles.table_body_rational, [styles.conditional_formatting_less_than,
                                                                styles.conditional_formatting_greater_than]))

    #### output ####

    # set compressed names (type_YYYY)
    df_subset.columns = compress_column_labels(df_subset.columns)

    form = TrialSiteFormular(TrialSite(df_subset, trial_site.metadata), output_file, formulae_columns)
    form.create()
