from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QMainWindow, QWidget, QVBoxLayout

from .InputHandler import InputHandler


class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        title = QLabel('Formular erstellen')
        title_font = title.font()
        title_font.setPointSize(24)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        input_handler = InputHandler()

        self.main_layout.addWidget(title)
        self.main_layout.addWidget(input_handler)


class MainWindow(QMainWindow):
    notification = Signal(str)

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('Neues Formular erstellen')
        self.setCentralWidget(MainUI())
