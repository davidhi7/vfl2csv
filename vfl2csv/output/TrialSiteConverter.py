import datetime
from typing import Optional
from pathlib import Path

import pandas as pd

import config

HierarchicalColumnLabel = tuple[datetime.date | datetime.datetime | str, str, str, str]


class TrialSite:
    def __init__(self, df: pd.DataFrame, metadata: dict[str, str]):
        self.df = df
        self.metadata = metadata

    def refactor_dataframe(self) -> None:
        """
        Refactor the dataframe. Transfer the input format into the required output format by renaming and rearranging
        columns as well as modifying the data types of the dataframe.
        """
        '''
        Rename columns: The first three columns contain the tree population (Bestandeseinheit), tree species (Baumart)
        and tree id (Baumnummer), followed by measurements. For each measurement recording, there are at least three columns:
         1. D: Durchmesser / diameter
         2. Aus: Ausscheidungskennung / reason why a tree ceased to stand in the trial site
         3. H: Höhe / height
        Additional measurement columns may also be included and declared in the config/columns.json file.

        The header part of the input files has four levels:
         1. date on which measurements where taken
         2. type of measurement (see above)
         3. measurement unit (e.g. meters, abbreviated as m)
         4. number of non NA values in this column
        The 3. and 4. row are not important, the 1. and 2. form together the new column name in the format 'YYYY-ABC'
        where YYYY is the year when the measurements where taken and ABC is the type of measurement, so one of D, Aus and H.
        
        The entire column specification as well as the corresponding data types are declared in the config/columns.json file. 
        '''
        head_column_count = len(config.column_layout['head'])
        measurement_fields_count = len(config.column_layout['measurements'])

        column_count = len(self.df.columns)
        measurement_column_count = column_count - head_column_count
        if measurement_column_count % measurement_fields_count != 0 or column_count < head_column_count:
            raise ValueError('Invalid column count')
        measurement_count = measurement_column_count // measurement_fields_count

        dtypes_mapping = {
            'string': pd.StringDtype(),
            'uint8': pd.UInt8Dtype(),
            'uint16': pd.UInt16Dtype(),
            'uint32': pd.UInt32Dtype(),
            'float64': pd.Float64Dtype()
        }

        new_column_names = list()
        for i, column in enumerate(self.df.columns[0:head_column_count]):
            head_column_template = config.column_layout['head'][i]
            new_column_names.append(head_column_template['override_name'])
            self.df[column] = self.df[column].astype(dtypes_mapping[head_column_template['type']])

        for measurement_index in range(measurement_count):
            column_shift = head_column_count + measurement_index * measurement_fields_count
            for i, column_hierarchy in enumerate(self.df.columns[column_shift:column_shift + measurement_fields_count]):
                measurement_column_template = config.column_layout['measurements'][i]
                new_column_names.append(
                    self.simplify_measurement_column_labels(column_hierarchy, measurement_column_template['override_name'])
                )
                self.df[column_hierarchy] = self.df[column_hierarchy].astype(
                    dtypes_mapping[measurement_column_template['type']]
                )
        self.df.columns = new_column_names

    @staticmethod
    def simplify_measurement_column_labels(hierarchy: HierarchicalColumnLabel, override_name: Optional[str]) -> str:
        """
        Reformat measurement column labels for the dataframe.
        See comments of #parse_data for more explanations
        :param hierarchy: Tuple consisting of four values
        :param override_name: If not None, use this as measurement name prefix instead of the prefix provided in the
        column hiearchy.
        :return: simplified label matching the requirements
        """
        if isinstance(hierarchy[0], datetime.datetime) or isinstance(hierarchy[0], datetime.date):
            date = hierarchy[0]
        else:
            try:
                date = datetime.datetime.strptime(hierarchy[0], '%d.%m.%Y')
            except ValueError as err:
                raise ValueError(
                    f'Measurement date {hierarchy[0]} does not match the expected format "dd.mm.YYYY"!') from err

        measurement_type = override_name if override_name is not None else hierarchy[1]

        return f'{measurement_type}_{date.year - (0 if date.month > 5 else 1)}'

    def replace_metadata_keys(self, pattern: Path | str) -> Path | str:
        """
        Return the given string with metadata keys being replaced with the corresponding values.
        Metadata keys wrapped in curly brackets are replaced with the corresponding value.
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

    def write_data(self, filepath: Path) -> None:
        """
        Write data formatted in CSV to the provided filepath.
        :param filepath: File path to save the data to
        """
        self.df.to_csv(filepath, na_rep='NA', sep=',', index=False)

    def write_metadata(self, filepath: Path) -> None:
        """
        Write extracted metadata formatted in simple key="value" pairs to the provided filepath.
        :param filepath: File path to save the metadata to
        """
        with open(filepath, 'w') as file:
            file.writelines([f'{key}={value}\n' for key, value in self.metadata.items()])
