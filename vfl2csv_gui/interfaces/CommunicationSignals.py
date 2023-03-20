from PySide6.QtCore import Signal


class CommunicationSignals:
    """
    Wrapper for signals used for communication between the GUI and worker instances.
    """
    progress = Signal(str)
    finished = Signal()
    error = Signal(Exception)
