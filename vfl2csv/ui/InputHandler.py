from pathlib import Path

from vfl2csv import batch_converter
from vfl2csv.input.InputData import InputData
from vfl2csv_gui.interfaces.AbstractInputHandler import AbstractInputHandler


class InputHandler(AbstractInputHandler):
    def __init__(self):
        super().__init__()
        self.input_data: list[InputData] = []
        self.input_files: list[Path] = []

    def clear(self) -> None:
        self.input_files = []
        self.input_data = []

    def __len__(self):
        return self.input_data.__len__()

    def load_input(self, input_paths: str | Path | list[str | Path]) -> None:
        self.input_files, self.input_data = batch_converter.find_input_data(input_paths)

    def convert(self, output_file: Path):
        # TODO impl
        ...

    def table_representation(self) -> list[list[str]]:
        return [[data.string_representation(short=True)] for data in self.input_data]
