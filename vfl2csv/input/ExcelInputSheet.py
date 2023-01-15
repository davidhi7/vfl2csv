from pathlib import Path
from typing import Iterable

import pandas as pd

from vfl2csv.input.ExcelWorkbook import ExcelWorkbook
from vfl2csv.input.InputFile import InputFile
from vfl2csv_base.TrialSite import TrialSite


class ExcelInputSheet(InputFile):
    def __init__(self, workbook: ExcelWorkbook, sheet_name: str):
        """
        Create a new Excel output file object.
        This class acts as abstraction for parsing Excel output files and acts as the interface between Excel and the
        TrialSite class, which represents measurement and metadata in a common format.
        ;param workbook: ExcelWorkbook instance
        :param sheet_name: Name of the sheet containing all trial site data
        """
        self.trial_site = None
        self.file_path = workbook.path
        self.open_workbook = workbook.open_workbook
        self.input_stream = workbook.in_mem_file
        self.sheet_name = sheet_name

    def parse(self) -> None:
        # extract metadata saved in the columns A5:A11 in a 'key : value' format
        metadata = dict()
        sheet = self.open_workbook[self.sheet_name]
        # less legible syntax:
        for row in sheet['A5:A11']:
            key, value = row[0].value.split(':')
            metadata[key.strip()] = value.strip()

        df = pd.read_excel(self.input_stream, sheet_name=self.sheet_name, header=list(range(0, 4)), skiprows=13)

        self.trial_site = TrialSite(df, metadata)

    def get_trial_site(self) -> TrialSite:
        return self.trial_site

    def __str__(self):
        return f'{self.file_path}#{self.sheet_name}'

    @staticmethod
    def iterate_files(input_files: Iterable[Path]) -> list['ExcelInputSheet']:
        workbooks = list(ExcelWorkbook(path) for path in input_files)
        input_sheets = list()
        for workbook in workbooks:
            input_sheets.extend(ExcelInputSheet(workbook, sheet_name) for sheet_name in workbook.sheets)
        return input_sheets
