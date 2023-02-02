from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot, QRunnable
from pandas import ExcelWriter

from vfl2csv_base.TrialSite import TrialSite
from vfl2csv_forms import trial_site_conversion
from vfl2csv_forms.excel import styles


class ConversionStateSignals(QObject):
    """
    `ConversionWorker` is a QRunnable and not a QObject, consequently it can't handle signals.
    Multiple inheritance is not possible in PySide6 for reasons unknown to me.
    This helper class inherits QObject and wraps the required signals for communication.
    """
    progress = Signal(str)
    finished = Signal()


class ConversionWorker(QRunnable):
    def __init__(self, trial_sites: list[TrialSite], output_file: Path):
        super().__init__()
        self.trial_sites = trial_sites
        self.output_file = output_file
        self.state = ConversionStateSignals()

    @Slot()
    def run(self) -> None:
        try:
            self.output_file.touch(exist_ok=True)
        except Exception as err:
            raise ValueError(f'Provided output file {self.output_file} cannot be created') from err

        trial_site_forms = []
        with ExcelWriter(self.output_file, engine='openpyxl') as writer:
            workbook = writer.book
            styles.register(workbook)
            for trial_site in self.trial_sites:
                trial_site_form = trial_site_conversion.convert(trial_site, self.output_file)
                trial_site_forms.append(trial_site_form)
                trial_site_form.init_worksheet(writer)
                trial_site_form.create(workbook)
                self.state.progress.emit(str(trial_site))
        self.state.finished.emit()
