from pathlib import Path

import pandas as pd

from input.InputFile import InputFile
from TrialSiteConverter import TrialSite


class TSVInputFile(InputFile):
    def __init__(self, file_path: Path):
        """
        Create a new TSV input file object.
        This class acts as abstraction for parsing TSV (tab-separated values) input files and acts as the interface between TSV and the
        TrialSite class, which represents measurement and metadata in a common format.
        :param file_path: Path object leading to the input file
        """
        self.trial_site = None
        self.file_path = file_path

    def parse(self) -> None:
        # TODO encoding?
        file_stream = open(self.file_path, 'r', encoding='iso8859_15')
        # skip first 4 rows
        metadata = dict()
        for _ in range(4):
            file_stream.readline()
        # read following 5 rows containing one key-value-pair each
        for _ in range(5):
            key, value = file_stream.readline().split(':')
            metadata[key.strip()] = value.strip()
        # move back to start of the stream
        file_stream.seek(0)

        df = pd.read_csv(file_stream, sep='\t', skiprows=13, header=list(range(0, 4)))
        # this last column is only created by pandas because in the input format, each row ends with one tabulator instead of the last value
        # consequently, this last column does not contain any values and needs to be removed.
        df = df.drop(columns=df.columns[-1])
        self.trial_site = TrialSite(df, metadata)

    def __str__(self) -> str:
        return str(self.file_path)

    def get_trial_site(self) -> TrialSite:
        return self.trial_site
