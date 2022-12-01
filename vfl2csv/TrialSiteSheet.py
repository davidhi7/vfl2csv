from pathlib import Path
import openpyxl
import pandas as pd


class TrialSiteSheet:
    def __init__(self, filepath: Path, sheet_name: str):
        self.filepath = filepath
        self.sheet_name = sheet_name
        self.metadata = self.parse_metadata()
        self.data = self.parse_data()

    def parse_metadata(self):
        """
        Parse the metadata from the Excel file.
        :return: Dict
        """
        # open excel file directly to extract metadata
        excel_file = openpyxl.load_workbook(filename=self.filepath, read_only=True)
        sheet = excel_file[self.sheet_name]

        # extract metadata saved in the columns A5:A11 in a 'key : value' format
        metadata = dict()
        for row in sheet.iter_rows(min_row=5, max_row=11, min_col=1, max_col=1, values_only=True):
            key, value = row[0].split(':')
            metadata[key.strip()] = value.strip()
        return metadata

    def parse_data(self):
        """
        Parse the measurement data from the Excel file and return it in the target format.
        :return: DataFrame
        """
        # Read the file again, this time using pandas to create dataframe directly.
        # Everything before row 14 is only metadata that is being handled in a different function.
        df = pd.read_excel(self.filepath, sheet_name=self.sheet_name, header=list(range(0, 4)), skiprows=13)
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
        # TODO: more elaborate column indexing: dont use only year, but also take growing season into account
        # noinspection PyTypeChecker
        df.columns = (
            'Bestandeseinheit',
            'Baumart',
            'Baumnummer',
            *[f'{multi_index[1]}_{multi_index[0].year}' for multi_index in df.columns[3:]]
        )

        # Also, the first column 'Bestandeseinheit' / tree population id is not actually needed, so let's discard it
        df = df.drop(columns='Bestandeseinheit')
        return df

    def write_data(self, filepath: Path):
        self.data.to_csv(filepath, na_rep='NA', index=False)

    def write_metadata(self, filepath: Path):
        with open(filepath, 'w') as file:
            file.writelines([f'{key}="{value}"\n' for key, value in self.metadata.items()])
