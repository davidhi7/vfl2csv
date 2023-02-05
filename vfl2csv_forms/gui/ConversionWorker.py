import logging
import traceback
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot, QRunnable
from pandas import ExcelWriter

from vfl2csv_base.TrialSite import TrialSite
from vfl2csv_forms import trial_site_conversion
from vfl2csv_forms.excel import styles

logger = logging.getLogger(__name__)


class ConversionStateSignals(QObject):
    """
    `ConversionWorker` is a QRunnable and not a QObject, consequently it can't handle signals.
    Multiple inheritance is not possible in PySide6 for reasons unknown to me.
    This helper class inherits QObject and wraps the required signals for communication.
    """
    progress = Signal(str)
    finished = Signal()
    error = Signal(Exception)


class ConversionWorker(QRunnable):
    def __init__(self, trial_sites: list[TrialSite], output_file: Path):
        super().__init__()
        self.trial_sites = trial_sites
        self.output_file = output_file
        self.state = ConversionStateSignals()

    @Slot()
    def run(self) -> None:
        self.output_file.touch(exist_ok=True)

        trial_site_forms = []
        with ExcelWriter(self.output_file, engine='openpyxl') as writer:
            try:
                workbook = writer.book
                styles.register(workbook)
                for trial_site in self.trial_sites:
                    trial_site_form = trial_site_conversion.convert(trial_site, self.output_file)
                    trial_site_forms.append(trial_site_form)
                    trial_site_form.init_worksheet(writer)
                    trial_site_form.create(workbook)
                    self.state.progress.emit(str(trial_site))
            except Exception as err:
                logger.error(err)
                logger.error(traceback.format_exc())
                self.state.error.emit(err)
        self.state.finished.emit()
