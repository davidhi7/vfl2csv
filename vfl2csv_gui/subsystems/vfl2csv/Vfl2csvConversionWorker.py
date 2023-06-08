import logging
import traceback
from pathlib import Path

from PySide6.QtCore import QRunnable, Slot

from vfl2csv import batch_converter
from vfl2csv_gui.interfaces.CommunicationSignals import CommunicationSignals
from vfl2csv_base.exceptions.ExceptionReport import ExceptionReport
from vfl2csv_gui.subsystems.forms.FormsInputHandler import InputHandler as FormsInputHandler

logger = logging.getLogger(__name__)


class ConversionWorker(QRunnable):
    def __init__(self, output_dir: Path, input_files: list[Path], create_form: bool):
        super().__init__()
        self.output_dir = output_dir
        self.input_files = input_files
        self.signals = CommunicationSignals()

        self.setting_create_form = create_form

    def handle_progress(self, value):
        if value is not None:
            self.signals.progress.emit(value)

    def create_form(self, trialsite_metadata_files: list[Path]) -> CommunicationSignals:
        forms_input_handler = FormsInputHandler()
        forms_input_handler.load_input(trialsite_metadata_files)
        return forms_input_handler.convert(self.output_dir / 'form.xlsx')[1]

    @Slot()
    def run(self) -> None:
        try:
            success, report = batch_converter.run(self.output_dir, self.input_files, on_progress=self.handle_progress)
            if success:
                if self.setting_create_form:
                    if len(report['metadata_output_files']) != len(self.input_files):
                        raise ValueError('Count of gathered trial site metadata files does not match count of input '
                                         'files')
                    signals = self.create_form(report['metadata_output_files'])
                    signals.progress.connect(self.signals.progress.emit)
                    signals.error.connect(self.signals.error.emit)
                    signals.finished.connect(lambda _: self.signals.finished.emit)
                    return
                else:
                    self.signals.finished.emit()
                    return
            if len(report['exceptions']) > 1:
                # providing one of potential many exceptions should be enough
                self.signals.error.emit(report['exceptions'][0])
            elif report.get('verification_error') is not None:
                self.signals.error.emit(report['verification_error'])
            else:
                raise
        except Exception as exception:
            logger.error(exception)
            exception_traceback = traceback.format_exc()
            logger.error(exception_traceback)
            self.signals.error.emit(ExceptionReport(exception, exception_traceback))
