import argparse
import sys

from vfl2csv.__main__ import start as vfl2csv_start
from vfl2csv_gui import MainWindow

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="vfl2csv_gui",
        description="GUI frontend for vfl2csv file conversion and form generation",
    )
    parser.add_argument("--cli", action="store_true", help="run vfl2csv in CLI mode")
    parsed_args, remaining_args = parser.parse_known_args()
    if vars(parsed_args)["cli"]:
        sys.exit(vfl2csv_start(remaining_args))
    MainWindow.start()
