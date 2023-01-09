from PySide6.QtWidgets import QFrame


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFixedHeight(20)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
