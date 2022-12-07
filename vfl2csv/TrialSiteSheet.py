import io
from pathlib import Path
import openpyxl
import pandas as pd


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
        Rename columns: The first three columns provide the tree population, tree species and tree id, then measurements follow.
        For each measurement recording, there are three columns:
         1. D: Durchmesser / diameter
         2. Aus: Ausscheidungskennung / reason why a tree ceased to stand in the trial site
         3. H: Höhe / height
        
        Turns out, there are four header rows:
         1. date on which measurements where taken
         2. type of measurement (see above)
         3. unit of the measurement
         4. number of measurements
        The 3. and 4. row are not important, the 1. and 2. form together the new column name in the format 'YYYY-XYZ'
        where YYYY is the year when the measurements where taken and XYZ is the type of measurement, so one of D, Aus and H. 
        PyCharm reports a wrong type missmatch, so let's supress that:
        '''
        # noinspection PyTypeChecker
        # TODO: column labels using years: research how to take growing seasons into account
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
        return f'{hierarchy[1]}_{hierarchy[0].year - (0 if hierarchy[0].month > 6 else 1)}'

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
