import datetime
import sys
from pathlib import Path
import json

from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.workbook import Workbook

import pandas as pd

if __name__ == '__main__':

    # config file that contains column information
    with open('config/columns.json', 'r') as file:
        column_layout = json.load(file)

    # parse input file
    input_file = Path(sys.argv[1])
    input_metadata_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])
    df = pd.read_csv(input_file)

    # counts of head/tree metadata columns
    head_column_count = len(column_layout['head'])
    # count of columns per record
    measurements_column_count = len(column_layout['measurements'])

    # create a new index to work with: first value in multi index is the record year, second value is the measurement value
    # for head columns, first value is empty, while the second value is the original column label
    multi_index = [('', col) for col in df.columns[:head_column_count]]
    # while creating the multi index, also determine the latest record year. This year's data will be part of the formular.
    latest_year = 0
    for i, column in enumerate(df.columns[head_column_count:]):
        record_attribute, record_year = column.split('_')
        record_year = int(record_year)
        multi_index.append((record_year, record_attribute))
        latest_year = max(latest_year, record_year)
    # assign the multi index
    df.columns = multi_index

    head_attributes = list(map(lambda x: x['override_name'], column_layout['head']))
    record_attributes = list(map(lambda x: x['override_name'], column_layout['measurements']))

    # labels of columns to be included into the formular
    column_selection = list([('', attribute) for attribute in head_attributes]) + list([(latest_year, attribute) for attribute in record_attributes])

    # create a subset of df containing only relevant columns
    df_subset = df[column_selection]
    # filter out all rows that have no value in any record attribute
    df_subset = df_subset[df_subset.notnull().sum(axis='columns') > head_column_count]

    # add new columns for each record attribute with the current year
    current_year = datetime.date.today().year
    for attribute in record_attributes:
        index = df_subset.columns.get_loc((latest_year, attribute)) + 1
        df_subset.insert(index, (current_year, attribute), pd.NA)

    wb = Workbook()

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_subset.to_excel(writer)

    """
    for r in dataframe_to_rows(df_subset, index=False, header=True):
        ws.append(r)
    wb.save('out/test.xlsx')
    """
