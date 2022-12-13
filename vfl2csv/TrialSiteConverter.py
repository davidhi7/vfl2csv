import datetime
import logging
import os
from pathlib import Path

import pandas as pd

from input.InputFile import InputFile


def trial_site_pipeline(input_batch: list[InputFile], output_data_pattern: Path, output_metadata_pattern: Path, process_index: int) -> None:
    logger = logging.getLogger(f'process {process_index}')
    for trial_site_input in input_batch:
        logger.info(f'Converting input {str(trial_site_input)}')
        trial_site_input.parse()
        trial_site = trial_site_input.get_trial_site()
        trial_site.refactor_dataframe()

        # write data
        data_output = trial_site.replace_metadata_keys(output_data_pattern)
        os.makedirs(data_output.parent, exist_ok=True)
        trial_site.write_data(data_output)

        # write metadata
        metadata_output = trial_site.replace_metadata_keys(output_metadata_pattern)
        os.makedirs(metadata_output.parent, exist_ok=True)
        trial_site.write_metadata(metadata_output)


class TrialSite:
    def __init__(self, df: pd.DataFrame, metadata: dict[str, str]):
        self.df = df
        self.metadata = metadata

    def refactor_dataframe(self) -> None:
        """
        Refactor the dataframe: transfer the input format into the required output format by renaming and rearranging columns.
        """
        '''
        Rename columns: The first three columns provide the tree population (Bestandeseinheit), tree species (Baumart)
        and tree id (Baumnummer), then measurements follow. For each measurement recording, there are three columns:
         1. D: Durchmesser / diameter
         2. Aus: Ausscheidungskennung / reason why a tree ceased to stand in the trial site
         3. H: Höhe / height

        Turns out, there are four header rows:
         1. date on which measurements where taken
         2. type of measurement (see above)
         3. unit of the measurement
         4. number of measurements
        The 3. and 4. row are not important, the 1. and 2. form together the new column name in the format 'YYYY-ABC'
        where YYYY is the year when the measurements where taken and ABC is the type of measurement, so one of D, Aus and H. 
        '''
        self.df.columns = (
            'Bestandeseinheit',
            'Baumart',
            'Baumnummer',
            *[self.simplify_column_labels(multi_index) for multi_index in self.df.columns[3:]]
        )

        # Also, the first column 'Bestandeseinheit' / tree population id is not actually needed, so let's discard it
        self.df = self.df.drop(columns='Bestandeseinheit')

    @staticmethod
    def simplify_column_labels(hierarchy: tuple[str]) -> str:
        """
        Reformat measurement column labels for the dataframe.
        See comments of #parse_data for more explanations
        :param hierarchy: Tuple consisting of four values
        :return: simplified label matching the requirements
        """
        if isinstance(hierarchy[0], datetime.datetime):
            date = hierarchy[0]
        else:
            try:
                date = datetime.datetime.strptime(hierarchy[0], '%d.%m.%Y')
            except ValueError as err:
                raise ValueError(f'Measurement date {hierarchy[0]} does not match the expected format "dd.mm.YYYY"!') from err

        measurement_type = hierarchy[1]
        if measurement_type not in ('D', 'H', 'Aus'):
            raise ValueError(f'Measurement type {measurement_type} is not one of "D", "H", or "Aus"!')

        return f'{hierarchy[1]}_{date.year - (0 if date.month > 5 else 1)}'

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
        :return:
        """
        self.df.to_csv(filepath, na_rep='NA', index=False)

    def write_metadata(self, filepath: Path) -> None:
        """
        Write extracted metadata formatted in simple key="value" pairs to the provided filepath.
        :param filepath: File path to save the metadata to
        :return:
        """
        with open(filepath, 'w') as file:
            file.writelines([f'{key}={value}\n' for key, value in self.metadata.items()])
