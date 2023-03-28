import sys

from PySide6.QtWidgets import QApplication

from vfl2csv_gui.components.BaseGui import BaseGui
from vfl2csv_gui.subsystems.forms import forms_gui_config
from vfl2csv_gui.subsystems.forms.FormsInputHandler import InputHandler

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = BaseGui(config=forms_gui_config, input_handler=InputHandler())
    ui.show()
    sys.exit(app.exec())
