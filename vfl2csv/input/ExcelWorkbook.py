import io
from pathlib import Path

import openpyxl


class ExcelWorkbook:
    def __init__(self, path: Path):
        """
        Create Excel workbook object. The Excel file at the given path is opened and sheet names are extracted.
        :param path: Path to the Excel file
        """
        self.path = path

        # read file into memory to not have to load the file repeatedly with openpyxl and pandas
        with open(path, 'rb') as file:
            self.in_mem_file = io.BytesIO(file.read())

        self.open_workbook = openpyxl.load_workbook(self.in_mem_file)
        self.sheets = self.open_workbook.sheetnames
