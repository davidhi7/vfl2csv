from pathlib import Path

from PySide6.QtCore import QObject

from vfl2csv_gui.interfaces.CommunicationSignals import CommunicationSignals


# let's suppose this is an abstract class
class AbstractInputHandler(QObject):
    def load_input(self, input_paths: str | Path | list[str | Path]) -> None: ...

    def convert(self, output_file: Path, settings: dict[str, bool] = None) -> CommunicationSignals: ...

    def __len__(self) -> int: ...

    def sort(self) -> None: ...

    def clear(self) -> None: ...

    def table_representation(self) -> list[list[str]]: ...
