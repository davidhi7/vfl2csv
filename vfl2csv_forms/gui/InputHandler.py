import logging
from pathlib import Path

from PySide6.QtCore import QObject, QThreadPool

from vfl2csv_base.TrialSite import TrialSite
from vfl2csv_base.errors.FileParsingError import FileParsingError
from vfl2csv_forms import config
from vfl2csv_forms.gui.ConversionWorker import ConversionWorker

logger = logging.getLogger(__name__)


class InputHandler(QObject):

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
                logger.error(f'Error during reading file {input_paths}', exc_info=True)
                raise ValueError(f'Error during reading file {input_paths}') from err

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

    def clear(self) -> None:
        self.trial_sites.clear()

    def __len__(self) -> int:
        return len(self.trial_sites)

    def convert(self, output_file: Path):
        worker = ConversionWorker(self.trial_sites, output_file)
        QThreadPool.globalInstance().start(worker)
        return worker.state.progress, worker.state.finished, worker.state.error
