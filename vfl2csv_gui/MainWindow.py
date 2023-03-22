from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from vfl2csv_gui.components.BaseGui import BaseGui
from vfl2csv_gui.subsystems.forms import forms_gui_config
from vfl2csv_gui.subsystems.forms.FormsInputHandler import InputHandler as FormsInputHandler
from vfl2csv_gui.subsystems.vfl2csv import vfl2csv_gui_config
from vfl2csv_gui.subsystems.vfl2csv.Vfl2csvInputHandler import InputHandler as Vlf2csvInputHandler


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        tab_widget = QTabWidget()

        forms_ui = BaseGui(config=forms_gui_config,
                           input_handler=FormsInputHandler())

        vfl2csv_ui = BaseGui(config=vfl2csv_gui_config,
                             input_handler=Vlf2csvInputHandler())

        tab_widget.addTab(forms_ui, 'Formulare')
        tab_widget.addTab(vfl2csv_ui, 'Konvertierung')
        layout.addWidget(tab_widget)
        self.setLayout(layout)
