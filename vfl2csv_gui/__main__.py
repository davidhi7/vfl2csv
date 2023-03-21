import sys

from PySide6.QtWidgets import QApplication

from vfl2csv_gui.MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    # main_window.setFixedWidth(main_window.width())
    # main_window.setFixedHeight(500)
    sys.exit(app.exec())
