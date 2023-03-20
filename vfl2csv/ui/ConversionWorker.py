from PySide6.QtCore import QRunnable, Slot


class ConversionWorker(QRunnable):
    def __init__(self):
        super().__init__()
        ...

    @Slot
    def run(self) -> None:
        ...
