import io
import logging
import os
from pathlib import Path

import openpyxl
import pandas as pd

from ExcelWorksheet import ExcelWorksheet


def worksheet_pipeline(excel_worksheet_batch: list[ExcelWorksheet], output_dir: Path, process_index: int) -> None:
    logger = logging.getLogger(str(process_index))
    for worksheet in excel_worksheet_batch:
        logger.info(f'Converting sheet {worksheet.workbook_path.name}#{worksheet.name}')
        trial_site_sheet = TrialSiteSheet(open_workbook=worksheet.workbook, input_file=worksheet.in_mem_file, sheet_name=worksheet.name)
        trial_site_folder = Path(trial_site_sheet.replace_metadata_keys(str(output_dir / '{revier}/{versuch}/')))
        # trial_site_folder = Path(output_dir / worksheet.name)
        os.makedirs(trial_site_folder, exist_ok=True)
        trial_site_sheet.write_data(
            trial_site_folder / trial_site_sheet.replace_metadata_keys('{parzelle}.csv')
        )
        trial_site_sheet.write_metadata(trial_site_folder / trial_site_sheet.replace_metadata_keys('{parzelle}_metadata.txt'))


class TrialSiteSheet:
    def __init__(self, open_workbook: openpyxl.Workbook, input_file: io.BytesIO, sheet_name: str):
        """
        Create a new trial site sheet object.
        This class acts as abstraction for the low level work with different data formats.
        :param open_workbook: Already loaded openpyxl workbook from the input file
        :param input_file: BytesIO object containing the binary input file data
        :param sheet_name: Name of the sheet containing all trial site data
        """
        self.open_workbook = open_workbook
        self.input_file = input_file
        self.sheet_name = sheet_name
        self.metadata = self.parse_metadata()
        self.data = self.parse_data()

    def parse_metadata(self) -> dict[str, str]:
        """
        Parse the metadata from the Excel file.
        :return: Dict
        """
        # instead of loading from the BytesIO object over and over, just use the already loaded worksheet from __main__
        # excel_file = openpyxl.load_workbook(self.input_file)
        # sheet = excel_file[self.sheet_name]
        sheet = self.open_workbook[self.sheet_name]

        # extract metadata saved in the columns A5:A11 in a 'key : value' format
        metadata = dict()
        # less legible syntax:
        # for row in sheet.iter_rows(min_row=5, max_row=11, min_col=1, max_col=1, values_only=True):
        for row in sheet['A5:A11']:
            key, value = row[0].value.split(':')
            metadata[key.strip()] = value.strip()
        return metadata

    def parse_data(self) -> pd.DataFrame:
        """
        Parse the measurement data from the Excel file and return it in the target format.
        :return: DataFrame
        """
        # Read the file again, this time using pandas to create dataframe directly.
        # Everything before row 14 is only metadata that is being handled in a different function.
        df = pd.read_excel(self.input_file, sheet_name=self.sheet_name, header=list(range(0, 4)), skiprows=13)
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
        PyCharm reports a wrong type missmatch, so let's supress that:
        '''
        # noinspection PyTypeChecker
        df.columns = (
            'Bestandeseinheit',
            'Baumart',
            'Baumnummer',
            *[self.simplify_column_labels(multi_index) for multi_index in df.columns[3:]]
        )

        # Also, the first column 'Bestandeseinheit' / tree population id is not actually needed, so let's discard it
        df = df.drop(columns='Bestandeseinheit')
        return df

    @staticmethod
    def simplify_column_labels(hierarchy: tuple) -> str:
        """
        Reformat measurement column labels for the dataframe.
        See comments of #parse_data for more explanations
        :param hierarchy: Tuple consisting of four values
        :return: simplified label matching the requirements
        """
        return f'{hierarchy[1]}_{hierarchy[0].year - (0 if hierarchy[0].month > 5 else 1)}'

    def replace_metadata_keys(self, pattern: str) -> Path:
        """
        Return the given string with metadata keys being replaced with the corresponding values.
        Metadata keys wrapped in curly brackets are replaced with the corresponding value.
        E.g. When invoking this function with the parameter '{Forstamt}/', the return value is '1234 sample forstamt/'
        :param pattern: string containing a variable number of metadata keys
        :return: string with metadata values in place of the keys in the pattern
        """
        # wrap every key in curly brackets; get the items
        metadata_replacements = {f'{{{key}}}': value for key, value in self.metadata.items()}.items()
        for key, value in metadata_replacements:
            pattern = pattern.replace(key.lower(), value)
        return pattern

    def write_data(self, filepath: Path) -> None:
        """
        Write data formatted in CSV to the provided filepath.
        :param filepath: File path to save the data to
        :return:
        """
        self.data.to_csv(filepath, na_rep='NA', index=False)

    def write_metadata(self, filepath: Path) -> None:
        """
        Write extracted metadata formatted in simple key="value" pairs to the provided filepath.
        :param filepath: File path to save the metadata to
        :return:
        """
        with open(filepath, 'w') as file:
            file.writelines([f'{key}={value}\n' for key, value in self.metadata.items()])
