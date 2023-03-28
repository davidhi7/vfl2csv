from pathlib import Path
from typing import Iterable

import pandas as pd

from vfl2csv import setup
from vfl2csv.input.InputData import InputData
from vfl2csv_base.TrialSite import TrialSite


class TsvInputFile(InputData):
    def __init__(self, file_path: Path):
        """
        Create a new TSV output file object.
        This class acts as abstraction for parsing TSV (tab-separated values) output files and acts as the interface
        between TSV and the
        TrialSite class, which represents measurement and metadata in a common format.
        :param file_path: Path object leading to the output file
        """
        self.file_path = file_path

    def parse(self) -> TrialSite:
        file_stream = open(self.file_path, 'r', encoding=setup.config['Input'].get('tsv_encoding', 'utf_8'))
        # skip first 4 rows containing unused data
        metadata = dict()
        for _ in range(4):
            file_stream.readline()
        # read following 5 rows containing one key-value-pair each
        for _ in range(7):
            key, value = file_stream.readline().split(':')
            metadata[key.strip()] = value.strip()
        # move back to start of the stream
        file_stream.seek(0)

        df = pd.read_csv(file_stream, sep='\t', skiprows=14, header=list(range(0, 4)), decimal=',')
        # this last column is only created by pandas because in the output format, each row ends with one tabulator
        # instead of the last value. Consequently, this last column does not contain any values and needs to be removed.
        df = df.drop(columns=df.columns[-1])
        return TrialSite(df, metadata)

    def string_representation(self, short=False):
        if short:
            return str(self.file_path.name)
        return str(self.file_path)

    def __str__(self) -> str:
        return self.string_representation()

    @staticmethod
    def iterate_files(files: Iterable[Path]) -> list[InputData]:
        return [TsvInputFile(file) for file in files]
