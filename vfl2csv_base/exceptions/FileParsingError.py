from pathlib import Path


class FileParsingError(Exception):
    def __init__(self, file: str | Path):
        self.file = str(file)
