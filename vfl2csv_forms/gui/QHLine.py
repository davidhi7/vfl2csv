from PySide6.QtWidgets import QFrame


# noinspection PyUnresolvedReferences
class QHLine(QFrame):
    """
    Simple horizontal line widget.
    Copied from https://stackoverflow.com/a/41068447
    """

    def __init__(self):
        super(QHLine, self).__init__()
        self.setFixedHeight(15)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
