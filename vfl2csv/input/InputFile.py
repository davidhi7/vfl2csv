# This is no longer nececssary as of python 3.11, but on writing this I used python 3.10
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# prevent a circular import
if TYPE_CHECKING:
    from TrialSiteConverter import TrialSite


class InputFile(ABC):
    @abstractmethod
    def parse(self) -> None: pass

    @abstractmethod
    def get_trial_site(self) -> TrialSite:
        pass

    @abstractmethod
    def __str__(self) -> TrialSite:
        pass
