import logging
import traceback
from pathlib import Path

from PySide6.QtCore import QRunnable, Slot

from vfl2csv import batch_converter
from vfl2csv_gui.interfaces.CommunicationSignals import CommunicationSignals

logger = logging.getLogger(__name__)


class ConversionWorker(QRunnable):
    def __init__(self, output_dir: Path, input_files: list[Path]):
        super().__init__()
        self.output_dir = output_dir
        self.input_files = input_files
        self.signals = CommunicationSignals()

    def handle_progress(self, value):
        if value is not None:
            self.signals.progress.emit(value)

    @Slot()
    def run(self) -> None:
        try:
            success, report = batch_converter.run(self.output_dir,
                                                  self.input_files,
                                                  on_progress=self.handle_progress)
            if success:
                self.signals.finished.emit()
                return

            if len(report['errors']) > 1:
                # providing one of potential many errors should be enough
                self.signals.error.emit(report['errors'][0])
            elif report.get('verification_error') is not None:
                self.signals.error.emit(report['verification_error'])
            else:
                self.signals.error.emit(None)
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
            self.signals.error.emit(e)
