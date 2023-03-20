from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from vfl2csv import gui_text_map as vfl2csv_text
from vfl2csv.ui.InputHandler import InputHandler as Vlf2csvInputHandler
from vfl2csv_forms import gui_text_map as vfl2csv_forms_text
from vfl2csv_forms.ui.InputHandler import InputHandler as FormsInputHandler
from vfl2csv_gui.components.BaseConversionGui import GraphicalUI


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        tab_widget = QTabWidget()
        main_window = GraphicalUI(text_map=vfl2csv_forms_text,
                                  input_handler=FormsInputHandler(),
                                  output_file_format='xlsx')
        main_window2 = GraphicalUI(text_map=vfl2csv_text,
                                   input_handler=Vlf2csvInputHandler(),
                                   output_file_format='xlsx')
        tab_widget.addTab(main_window, 'Formulare')
        tab_widget.addTab(main_window2, 'Konvertierung')
        layout.addWidget(tab_widget)
        self.setLayout(layout)
