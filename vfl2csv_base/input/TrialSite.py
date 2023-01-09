from __future__ import annotations

from pathlib import Path

import pandas as pd


class TrialSite:
    def __init__(self, df: pd.DataFrame, metadata: dict[str, str]):
        self.df = df
        self.metadata = metadata

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

    @staticmethod
    def from_metadata_file(metadata_path: Path) -> TrialSite:
        if not metadata_path.is_file():
            raise ValueError(f'{metadata_path} is not a valid file')
        metadata = dict()
        with open(metadata_path, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                # use maxsplit to avoid removing equality symbols in the value
                key, value = line.split('=', maxsplit=1)
                # remove trailing newline in value
                metadata[key] = value.rstrip()

        df_path = metadata_path.parent / Path(metadata['DataFrame'])
        if not df_path.is_file():
            raise ValueError(f'Relative path {Path(metadata["DataFrame"])} is not a valid file')
        df = pd.read_csv(df_path)
        return TrialSite(df, metadata)
