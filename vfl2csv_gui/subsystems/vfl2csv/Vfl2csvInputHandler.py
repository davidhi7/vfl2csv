from pathlib import Path

from PySide6.QtCore import QThreadPool

from vfl2csv import batch_converter
from vfl2csv.input.InputData import InputData
from vfl2csv_gui.interfaces.AbstractInputHandler import AbstractInputHandler
from vfl2csv_gui.interfaces.CommunicationSignals import CommunicationSignals
from vfl2csv_gui.subsystems.vfl2csv.Vfl2csvConversionWorker import Vfl2csvConversionWorker


class Vfl2csvInputHandler(AbstractInputHandler):

    def __init__(self):
        super().__init__()
        # InputData objects representing trial site data (e.g. TSV files orr Excel sheets)
        self.input_data: list[InputData] = []
        # Paths of the input files (e.g. TSV or Excel files)
        self.input_files: list[Path] = []

    def load_input(self, input_paths: str | Path | list[str | Path]) -> None:
        self.input_files, self.input_data = batch_converter.find_input_data(input_paths)

    def clear(self) -> None:
        self.input_files = []
        self.input_data = []

    def convert(self, output_dir: Path, settings: dict[str, bool] = None) -> tuple[int, CommunicationSignals]:
        setting_create_form = settings['setting_create_form']
        worker = Vfl2csvConversionWorker(output_dir, self.input_files, self.input_data, create_form=setting_create_form)
        QThreadPool.globalInstance().start(worker)
        steps = len(self.input_data) * 2 if setting_create_form else 1
        return steps, worker.signals

    def table_representation(self) -> list[list[str]]:
        return [[data.string_representation(short=True)] for data in self.input_data]

    def sort(self):
        self.input_data = sorted(self.input_data, key=lambda input_data: input_data.string_representation())

    def __len__(self):
        return len(self.input_data)
