from __future__ import annotations

import re
from pathlib import Path
from typing import Generator

import pandas as pd

from vfl2csv_base.ColumnScheme import ColumnScheme
from vfl2csv_base.datatypes_mapping import pandas_datatypes_mapping
from vfl2csv_base.exceptions.FileParsingError import FileParsingError

measurement_column_pattern = re.compile(r'^\D+_\d{4}$')


class TrialSite:
    def __init__(self, df: pd.DataFrame, metadata: dict[str, str]):
        self.df = df
        self.metadata = metadata

    def replace_metadata_keys(self, pattern: Path | str) -> Path | str:
        """
        Return the given string with metadata keys being replaced with the corresponding values.
        Lowercase Metadata keys wrapped in curly brackets are replaced with the corresponding value.
        E.g. When invoking this function with the parameter '{forstamt}/', the return value is '1234 sample forstamt/'
        :param pattern: string or Path containing a variable number of metadata keys
        :return: string with metadata values in place of the keys in the pattern
        """
        str_pattern = str(pattern)
        # wrap every key in curly brackets; get the items
        metadata_replacements = {f'{{{key}}}': value for key, value in self.metadata.items()}.items()
        for key, value in metadata_replacements:
            str_pattern = str_pattern.replace(key.lower(), value)
        if isinstance(pattern, Path):
            return Path(str_pattern)
        return str_pattern

    def verify_column_integrity(self, column_scheme: ColumnScheme) -> None:
        """
        Verify the integrity of the dataframe by comparing all column labels to the provided column scheme.
        Additionally, the datatypes are set according to the column scheme.
        :param column_scheme:
        :return:
        """
        head_column_count = len(column_scheme.head)
        measurements_type_count = len(column_scheme.measurements)

        # work only on a deep copy of the dataframe
        df = self.df.copy(deep=True)
        df.columns = list(self.expand_column_labels(df.columns))

        # verify head columns
        if head_column_count > 0:
            for i, column in enumerate(df.columns[:head_column_count]):
                if column[1] != column_scheme.head[i].get('override_name', column_scheme.head[i]['name']):
                    raise ValueError(
                        f'Column `{column[1]}` of the dataframe does not match the expected name provided in '
                        f'the columns.json file!')
                df[column] = df[column].astype(pandas_datatypes_mapping[column_scheme.head[i]['type']])

        # verify body columns
        # count of expected individual records with n columns each
        if measurements_type_count > 0:
            # noinspection PyTypeChecker
            measurement_count = (len(df.columns) - head_column_count) // measurements_type_count
            for measurement_index in range(measurement_count):
                for attribute_index in range(measurements_type_count):
                    column_index = head_column_count + measurement_index * measurements_type_count + attribute_index
                    column = df.columns[column_index]
                    if column[1] != column_scheme.measurements[attribute_index].get(
                            'override_name', column_scheme.measurements[attribute_index]['name']):
                        raise ValueError(
                            f'Column `{column[1]}_{column[0]}` of the dataframe does not match the expected '
                            f'name provided in the columns.json file!')
                    df[column] = df[column].astype(
                        pandas_datatypes_mapping[column_scheme.measurements[attribute_index]['type']])

        df.columns = self.compress_column_labels(df.columns)
        self.df = self.df.astype(df.dtypes)

    def __str__(self) -> str:
        return f'{self.metadata["Revier"]}/{self.metadata["Versuch"]}-{self.metadata["Parzelle"]}'

    @staticmethod
    def compress_column_labels(multi_index: list[tuple[int, str]]) -> Generator[str, None, None]:
        """
        Convert labels from the tuple `(year or -1, type)` into the string 'type_year'
        """
        for label in multi_index:
            if label[0] > 0:
                yield f'{label[1]}_{label[0]}'
            else:
                yield label[1]

    @staticmethod
    def expand_column_labels(index: list[str]) -> Generator[tuple[int, str], None, None]:
        """
        Convert labels from the string 'type_year' into the tuple `(year or -1, type)`
        """
        for label in index:
            if measurement_column_pattern.fullmatch(label):
                # Fix in case there are multiple underscores in one column name
                record_type, record_year = label.rsplit('_', maxsplit=1)
                yield int(record_year), record_type
            else:
                # for head columns, only use the original column label
                yield -1, label

    @staticmethod
    def from_metadata_file(metadata_path: Path) -> TrialSite:
        if not metadata_path.is_file():
            raise FileNotFoundError(f'{metadata_path} is not a valid file')
        metadata = dict()
        try:
            with open(metadata_path, 'r', encoding='utf-8') as file:
                for line in file.readlines():
                    # use maxsplit to avoid removing equality symbols in the value
                    key, value = line.split('=', maxsplit=1)
                    # remove trailing newline in value
                    metadata[key] = value.rstrip()
        except UnicodeDecodeError as err:
            raise FileParsingError(metadata_path) from err

        df_path = metadata_path.parent / Path(metadata['DataFrame'])
        if not df_path.is_file():
            raise FileParsingError(f'Relative path {Path(metadata["DataFrame"])} is not a valid file')
        df = pd.read_csv(df_path)
        return TrialSite(df, metadata)
