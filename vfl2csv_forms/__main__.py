import sys

from PySide6.QtWidgets import QApplication

from vfl2csv_gui.components.BaseGui import BaseGui
from vfl2csv_gui.subsystems.forms.forms_gui_config import forms_gui_config
from vfl2csv_gui.subsystems.forms.FormsInputHandler import FormsInputHandler

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = BaseGui(config=forms_gui_config, input_handler=FormsInputHandler())
    ui.show()
    sys.exit(app.exec())
