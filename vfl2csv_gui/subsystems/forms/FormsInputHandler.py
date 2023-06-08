import logging
from pathlib import Path

from PySide6.QtCore import QThreadPool

from vfl2csv_base.TrialSite import TrialSite
from vfl2csv_base.exceptions.FileParsingError import FileParsingError
from vfl2csv_forms import config
from vfl2csv_gui.interfaces.AbstractInputHandler import AbstractInputHandler
from vfl2csv_gui.interfaces.CommunicationSignals import CommunicationSignals
from vfl2csv_gui.subsystems.forms.FormsConversionWorker import ConversionWorker

logger = logging.getLogger(__name__)


class InputHandler(AbstractInputHandler):

    def __init__(self):
        super().__init__()
        self.trial_sites = []

    def load_input(self, input_paths: str | Path | list[str | Path]) -> None:
        if isinstance(input_paths, list):
            for path in input_paths:
                self.load_input(path)
            return
        path = Path(input_paths)
        if not path.exists():
            raise FileNotFoundError(str(path))

        if path.is_dir():
            if config['Input'].getboolean('directory_search_recursively', False):
                generator = path.rglob(config['Input'].get('metadata_search_pattern'))
            else:
                generator = path.glob(config['Input'].get('metadata_search_pattern'))
            for content in generator:
                self.load_input(content)
        elif path.is_file():
            try:
                path = Path(input_paths)
                self.trial_sites.append(TrialSite.from_metadata_file(path))
            except FileParsingError as err:
                logger.error(f'Error during reading file {err.file}', exc_info=True)
                self.trial_sites.clear()
                raise

    def clear(self) -> None:
        self.trial_sites.clear()

    def convert(self, output_file: Path, settings: dict[str, bool] = None) -> tuple[int, CommunicationSignals]:
        steps = len(self.trial_sites)
        worker = ConversionWorker(self.trial_sites, output_file)
        QThreadPool.globalInstance().start(worker)
        return steps, worker.signals

    def table_representation(self) -> list[list[str]]:
        return [[
            trial_site.metadata['Versuch'],
            trial_site.metadata['Parzelle']
        ] for trial_site in self.trial_sites]

    def sort(self) -> None:
        self.trial_sites = sorted(self.trial_sites, key=self.sort_decorate_trial_site)

    @staticmethod
    def sort_decorate_trial_site(trial_site: TrialSite) -> tuple[str, int]:
        trial = trial_site.metadata['Versuch'] or ''
        try:
            plot = int(trial_site.metadata['Parzelle'])
        except ValueError:
            plot = trial_site.metadata['Parzelle']
        return trial, plot

    def __len__(self):
        return len(self.trial_sites)
