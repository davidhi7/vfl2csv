import sys

from PySide6.QtWidgets import QApplication

from .gui.GraphicalUI import GraphicalUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = GraphicalUI()
    main_window.show()
    sys.exit(app.exec())
