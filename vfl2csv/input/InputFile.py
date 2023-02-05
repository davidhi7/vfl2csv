# This is no longer necessary as of python 3.11, but on writing this I used python 3.10
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from vfl2csv_base.TrialSite import TrialSite


class InputFile(ABC):
    @abstractmethod
    def parse(self) -> None: pass

    @abstractmethod
    def get_trial_site(self) -> TrialSite:
        pass

    @abstractmethod
    def __str__(self) -> TrialSite:
        pass

    @staticmethod
    @abstractmethod
    def iterate_files(files: Iterable[Path]) -> list[InputFile]:
        pass
