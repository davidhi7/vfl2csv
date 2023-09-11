# This is no longer necessary as of python 3.11, but on writing this I used python 3.10
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from vfl2csv_base.TrialSite import TrialSite


class InputData(ABC):
    def __init__(self, file_path: Path):
        self.file_path = file_path

    @abstractmethod
    def parse(self) -> TrialSite:
        ...

    @abstractmethod
    def __str__(self) -> TrialSite:
        ...

    @abstractmethod
    def string_representation(self, short=False):
        ...

    @staticmethod
    @abstractmethod
    def iterate_files(files: Iterable[Path]) -> list[InputData]:
        ...
