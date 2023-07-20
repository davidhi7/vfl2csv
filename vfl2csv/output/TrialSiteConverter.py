import datetime
import re
from pathlib import Path
from typing import Optional

from vfl2csv import setup
from vfl2csv_base.TrialSite import TrialSite
from vfl2csv_base.datatypes_mapping import pandas_datatypes_mapping as dtypes_mapping

HierarchicalColumnLabel = tuple[datetime.date | datetime.datetime | str, str, str, str]


class TrialSiteConverter:
    def __init__(self, trial_site: TrialSite):
        self.trial_site = trial_site

    def refactor_dataframe(self) -> None:
        """
        Refactor the dataframe. Transfer the output format into the required output format by renaming and rearranging
        columns as well as modifying the data types of the dataframe.
        Before doing so, it is verified that the input data matches the column counts provided in the ColumnScheme
        instance.
        """
        '''
        In the default configuration, the first three columns contain the tree population (Bestandeseinheit), tree
        species (Baumart) and tree id (Baumnummer), followed by measurements. For each measurement recording, there are
        at least three columns:
            1. D: diameter (Durchmesser)
            2. Aus: reason why a tree ceased to stand in the trial site ('Ausscheidungskennung')
            3. H: height (Höhe)
         Additional measurement columns may also be included and declared 
        in the config/columns.json file.

        The header part of the output files has four levels: 1. date on which measurements where taken 2. type of 
        measurement (see above) 3. measurement unit (e.g. meters, abbreviated as m) 4. number of non NA values in 
        this column The 3. and 4. row are not important, the 1. and 2. form together the new column name in the 
        format 'YYYY-ABC' where YYYY is the year when the measurements where taken and ABC is the type of 
        measurement, so one of D, Aus and H.
        
        The entire column specification as well as the corresponding data types are declared in the 
        config/columns.json file.'''
        # count of expected columns containing tree data
        head_column_count = len(setup.column_scheme.head)
        # count of expected measurement fields (different types of values)
        measurement_fields_count = len(setup.column_scheme.measurements)

        column_count = len(self.trial_site.df.columns)
        # count of all columns containing measurements
        measurement_column_count = column_count - head_column_count
        # `measurement_column_count` must be a multiple of `measurement_fields_count` and the count of all columns must
        # be at least the count of all head columns
        if measurement_column_count % measurement_fields_count != 0 or column_count < head_column_count:
            raise ValueError('Invalid column count')
        # count of all measurement recordings, so sets of every field
        measurement_count = measurement_column_count // measurement_fields_count

        # new column names are assigned later
        new_column_names = list()
        # first, iterate head columns
        for template, column in zip(setup.column_scheme.head, self.trial_site.df.columns[0:head_column_count]):
            # Check column name
            if column[3] != template['name']:
                raise ValueError(f'Head column `{template["name"]}` from template does not match corresponding input '
                                 f'column `{column[3]}`')
            # rename columns
            new_column_names.append(template.get('override_name', template['name']))
            # reassign datatype
            self.trial_site.df[column] = self.trial_site.df[column].astype(dtypes_mapping[template['type']])

        # iterate all measurements
        for measurement_index in range(measurement_count):
            # number of columns already refactored
            column_shift = head_column_count + measurement_index * measurement_fields_count
            # iterate all columns of the next measurement
            for template, column in zip(
                    setup.column_scheme.measurements,
                    self.trial_site.df.columns[column_shift:column_shift + measurement_fields_count]
            ):
                # Check column name
                if column[1] != template['name']:
                    raise ValueError(f'Measurement column `{template["name"]}` from template does not match '
                                     f'corresponding input column `{column[1]}`')
                # rename column
                new_column_names.append(
                    self.simplify_measurement_column_labels(column,
                                                            template.get('override_name', template['name']))
                )
                # reassign datatype
                self.trial_site.df[column] = self.trial_site.df[column].astype(
                    dtypes_mapping[template['type']]
                )
        self.trial_site.df.columns = new_column_names

    def trim_metadata(self) -> None:
        """
        Replace double whitespaces in metadata keys with simple spaces.
        :return:
        """
        for key, value in self.trial_site.metadata.items():
            self.trial_site.metadata[key] = re.sub(r'\s+', ' ', value)

    @staticmethod
    def simplify_measurement_column_labels(hierarchy: HierarchicalColumnLabel, override_name: Optional[str]) -> str:
        """
        Reformat measurement column labels for the dataframe.
        Simplify the tuple of four header values into one string
        See comments of #refactor_dataframe for more explanations
        :param hierarchy: Tuple consisting of four values
        :param override_name: If not None, use this as measurement name prefix instead of the prefix provided in the
        column hierarchy.
        :return: simplified label matching the requirements

        Not to confuse with `vfl2csv_base.Trialsite#compress_column_labels`, which only takes a tuple of two values as
        input column name
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

        # if the month is lower or equal to June, decrement the year to respect growing seasons
        return f'{measurement_type}_{date.year - (0 if date.month > 6 else 1)}'

    def write_data(self, filepath: Path) -> None:
        """
        Write data formatted in CSV to the provided filepath.
        :param filepath: File path to save the data to
        """
        self.trial_site.df.to_csv(filepath, na_rep='NA', sep=',', index=False, encoding='utf-8')

    def write_metadata(self, filepath: Path) -> None:
        """
        Write extracted metadata formatted in simple key="value" pairs to the provided filepath.
        :param filepath: File path to save the metadata to
        """
        with open(filepath, 'w', encoding='utf-8') as file:
            file.writelines([f'{key}={value}\n' for key, value in self.trial_site.metadata.items()])
