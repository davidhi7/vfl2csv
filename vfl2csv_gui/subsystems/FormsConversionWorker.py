import logging
import traceback
from pathlib import Path

from PySide6.QtCore import Slot, QRunnable
from pandas import ExcelWriter

from vfl2csv_base.TrialSite import TrialSite
from vfl2csv_forms import trial_site_conversion
from vfl2csv_forms.excel import styles
from vfl2csv_gui.interfaces.CommunicationSignals import CommunicationSignals

logger = logging.getLogger(__name__)


class ConversionWorker(QRunnable):
    def __init__(self, trial_sites: list[TrialSite], output_file: Path):
        super().__init__()
        self.trial_sites = trial_sites
        self.output_file = output_file
        self.signals = CommunicationSignals()

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
                    self.signals.progress.emit(str(trial_site))
            except Exception as err:
                logger.error(err)
                logger.error(traceback.format_exc())
                self.signals.error.emit(err)
        self.signals.finished.emit()
