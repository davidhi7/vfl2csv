from pathlib import Path

from vfl2csv_base.TrialSite import TrialSite


class FileParsingError(Exception):
    def __init__(self, file: str | Path, message: str | None = None):
        exception_text = f'Failed to parse file "{str(file)}": Invalid file format'
        if message:
            exception_text += '\n'
            exception_text += message
        super().__init__(exception_text)


class FileSavingError(Exception):
    def __init__(self, file: str | Path):
        super().__init__(f'Failed to save file "{str(file)}"')


class TrialSiteFormatError(Exception):
    def __int__(self, trial_site: TrialSite, message: str | None = None):
        exception_text = f'Failed to handle trial site "{str(trial_site)}": Invalid format'
        if message:
            exception_text += '\n'
            exception_text += message


class IllegalConfigError(Exception):
    pass
