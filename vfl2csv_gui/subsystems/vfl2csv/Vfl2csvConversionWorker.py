import logging
from pathlib import Path

from PySide6.QtCore import QRunnable

from vfl2csv import batch_converter
from vfl2csv.input.InputData import InputData
from vfl2csv_gui.interfaces.CommunicationSignals import CommunicationSignals
from vfl2csv_gui.subsystems.forms.FormsConversionWorker import FormsConversionHandler as FormsConversionWorker
from vfl2csv_gui.subsystems.forms.FormsInputHandler import FormsInputHandler as FormsInputHandler

logger = logging.getLogger(__name__)


class Vfl2csvConversionWorker(QRunnable):
    def __init__(self, output_dir: Path, input_files: list[Path], input_data: list[InputData], create_form: bool):
        super().__init__()
        self.output_dir = output_dir
        self.input_files = input_files
        self.input_data = input_data
        self.signals = CommunicationSignals()

        self.setting_create_form = create_form

    def handle_progress(self, value):
        if value is not None:
            self.signals.progress.emit(value)

    def run(self) -> None:
        try:
            report = batch_converter.run(self.output_dir, self.input_files, on_progress=self.handle_progress)
            if self.setting_create_form:
                forms_input_handler = FormsInputHandler()
                forms_input_handler.load_input(report['metadata_output_files'])
                # Run the form conversion worker in the same thread to prevent issues with different threads and signals
                forms_worker = FormsConversionWorker(forms_input_handler.trial_sites,
                                                     self.output_dir / 'aufnahmeformular.xlsx')

                forms_worker.signals.progress.connect(self.signals.progress)
                forms_worker.signals.error.connect(self.signals.error)
                forms_worker.signals.finished.connect(self.signals.finished)
                forms_worker.run()
            else:
                self.signals.finished.emit()
        except Exception as exception:
            logger.exception(msg='Error during vfl2csv conversion')
            self.signals.error.emit(exception)
