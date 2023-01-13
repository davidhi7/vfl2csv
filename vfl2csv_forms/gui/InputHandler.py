import logging
from pathlib import Path
from typing import Generator

from openpyxl.reader.excel import load_workbook
from pandas import ExcelWriter

from vfl2csv_base.input.TrialSite import TrialSite
from ..excel import styles
from ..trial_site_conversion import convert
from .. import config

logger = logging.getLogger(__name__)


class InputHandler:

    def __init__(self):
        self.trial_sites = []

    def load_input(self, input_paths: str | Path | list[str | Path]):
        if isinstance(input_paths, list):
            for path in input_paths:
                self.load_input(path)
            return
        path = Path(input_paths)
        if not path.exists():
            raise ValueError(f'File or directory {path} does not exist')

        if path.is_dir():
            for content in path.glob(config['Input'].get('metadata_search_pattern')):
                self.load_input(content)
            return
        elif path.is_file():
            try:
                path = Path(input_paths)
                self.trial_sites.append(TrialSite.from_metadata_file(path))
            except ValueError as err:
                logger.error(f'Error during reading file {input_paths}', exc_info=True)
                raise ValueError(f'Error during reading file {input_paths}') from err

    def sort(self):
        self.trial_sites = sorted(self.trial_sites, key=self.decorate_trial_site)

    @staticmethod
    def decorate_trial_site(trial_site: TrialSite) -> tuple[str, int]:
        trial = trial_site.metadata['Versuch'] or ''
        try:
            plot = int(trial_site.metadata['Parzelle'])
        except ValueError:
            plot = trial_site.metadata['Parzelle']
        return trial, plot

    def clear(self):
        self.trial_sites.clear()

    def __len__(self):
        return len(self.trial_sites)

    def createAll(self, output_file: Path, exist_ok=False) -> Generator[str, None, None]:
        try:
            output_file.touch(exist_ok=exist_ok)
        except Exception as err:
            raise ValueError(f'Provided output file {output_file} cannot be created') from err

        trial_site_forms = []
        with ExcelWriter(output_file, engine='openpyxl') as writer:
            for trial_site in self.trial_sites:
                print(trial_site.metadata)
                trial_site_form = convert(trial_site, output_file)
                trial_site_forms.append(trial_site_form)
                trial_site_form.init_worksheet(writer)
                yield trial_site_form.sheet_name

        workbook = load_workbook(output_file)
        styles.register(workbook)
        for trial_site_form in trial_site_forms:
            trial_site_form.create(workbook)
            yield 'done'
