from PySide6.QtCore import Signal, QObject


class CommunicationSignals(QObject):
    """
    Wrapper for signals used for communication between the GUI and worker instances.
    """
    progress = Signal(str)
    finished = Signal()
    error = Signal(Exception)
