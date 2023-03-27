import argparse
import sys

from PySide6.QtWidgets import QApplication

from vfl2csv.__main__ import start
from vfl2csv_gui.MainWindow import MainWindow

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='vfl2csv_gui',
        description='GUI frontend for vfl2csv file conversion and form generation'
    )
    parser.add_argument(
        '--cli',
        action='store_true',
        help='run vfl2csv in CLI mode'
    )
    parsed_args, remaining_args = parser.parse_known_args()
    if vars(parsed_args)['cli']:
        sys.exit(start(remaining_args))

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
