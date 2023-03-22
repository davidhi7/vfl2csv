from pathlib import Path

from PySide6.QtCore import QRunnable, Slot

from vfl2csv import batch_converter
from vfl2csv_gui.interfaces.CommunicationSignals import CommunicationSignals


class ConversionWorker(QRunnable):
    def __init__(self, output_dir: Path, input_files: list[Path]):
        super().__init__()
        self.output_dir = output_dir
        self.input_files = input_files
        self.signals = CommunicationSignals()

    @Slot()
    def run(self) -> None:
        batch_converter.run(self.output_dir, self.input_files)
        self.signals.finished.emit()
