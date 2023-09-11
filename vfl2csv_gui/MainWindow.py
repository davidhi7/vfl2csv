import sys

from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QApplication

from vfl2csv_gui.components.BaseGui import BaseGui
from vfl2csv_gui.subsystems.forms.FormsInputHandler import FormsInputHandler
from vfl2csv_gui.subsystems.forms.forms_gui_config import forms_gui_config
from vfl2csv_gui.subsystems.vfl2csv.Vfl2csvInputHandler import Vfl2csvInputHandler
from vfl2csv_gui.subsystems.vfl2csv.vfl2csv_gui_config import vfl2csv_gui_config


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        tab_widget = QTabWidget()

        vfl2csv_ui = BaseGui(
            config=vfl2csv_gui_config, input_handler=Vfl2csvInputHandler()
        )
        forms_ui = BaseGui(config=forms_gui_config, input_handler=FormsInputHandler())

        tab_widget.addTab(vfl2csv_ui, "Konvertierung")
        tab_widget.addTab(forms_ui, "Formulare")
        layout.addWidget(tab_widget)
        self.setLayout(layout)
        self.setWindowTitle("vfl2csv")


def start():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
