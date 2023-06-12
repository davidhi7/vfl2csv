import logging
import traceback
from pathlib import Path

from PySide6.QtCore import QRunnable, Slot

from vfl2csv import batch_converter
from vfl2csv_gui.interfaces.CommunicationSignals import CommunicationSignals
from vfl2csv_gui.subsystems.forms.FormsInputHandler import FormsInputHandler as FormsInputHandler
from vfl2csv_gui.subsystems.forms.FormsConversionWorker import FormsConversionHandler as FormsConversionWorker

logger = logging.getLogger(__name__)


class Vfl2csvConversionWorker(QRunnable):
    def __init__(self, output_dir: Path, input_files: list[Path], create_form: bool):
        super().__init__()
        self.output_dir = output_dir
        self.input_files = input_files
        self.signals = CommunicationSignals()

        self.setting_create_form = create_form

    def handle_progress(self, value):
        if value is not None:
            self.signals.progress.emit(value)

    def create_form(self, trial_site_metadata_files: list[Path]) -> CommunicationSignals:
        forms_input_handler = FormsInputHandler()
        forms_input_handler.load_input(trial_site_metadata_files)
        return forms_input_handler.convert(self.output_dir / 'form.xlsx')[1]

    def run(self) -> None:
        report = batch_converter.run(self.output_dir, self.input_files, on_progress=self.handle_progress)
        if self.setting_create_form:
            if len(report['metadata_output_files']) != len(self.input_files):
                raise ValueError('Count of gathered trial site metadata files does not match count of input files')
            forms_input_handler = FormsInputHandler()
            forms_input_handler.load_input(report['metadata_output_files'])
            forms_worker = FormsConversionWorker(forms_input_handler.trial_sites, self.output_dir / 'form.xlsx')
            # Run the form conversion worker in the same thread to prevent issues with different threads and signals
            # _, forms_signals = forms_input_handler.convert(self.output_dir / 'form.xlsx')

            forms_worker.signals.progress.connect(self.signals.progress)
            forms_worker.signals.error.connect(self.signals.error)
            # forms_worker.signals.finished.connect(self.signals.finished)
            forms_worker.run()
            self.signals.finished.emit()
        else:
            self.signals.finished.emit()

    # try:
        #     if success:
        #         if self.setting_create_form:
        #             if len(report['metadata_output_files']) != len(self.input_files):
        #                 raise ValueError('Count of gathered trial site metadata files does not match count of input '
        #                                  'files')
        #             signals = self.create_form(report['metadata_output_files'])
        #             signals.progress.connect(self.signals.progress.emit)
        #             signals.error.connect(self.signals.error.emit)
        #             signals.finished.connect(lambda _: self.signals.finished.emit)
        #             return
        #         else:
        #             self.signals.finished.emit()
        #             return
        #     if len(report['exceptions']) > 1:
        #         # providing one of potential many exceptions should be enough
        #         self.signals.error.emit(report['exceptions'][0])
        #     elif report.get('verification_error') is not None:
        #         self.signals.error.emit(report['verification_error'])
        #     else:
        #         raise
        # except Exception as exception:
        #     logger.error(exception)
        #     exception_traceback = traceback.format_exc()
        #     logger.error(exception_traceback)
        #     self.signals.error.emit(ExceptionReport(exception, exception_traceback))
