from argparse import ArgumentParser
from pathlib import Path

from vfl2csv_base import default_column_scheme_path

parser = ArgumentParser(
    prog='vfl2csv',
    description='Convert Versuchsflächendatenbanksystem-output into CSV files.'
)
parser.add_argument('--config', '-c',
                    action='store',
                    type=Path,
                    help='Path to the configuration file',
                    default='./config/config_vfl2csv.ini')
parser.add_argument('--column-scheme', '-C',
                    action='store',
                    type=Path,
                    help='Path to the column scheme configuration',
                    default=default_column_scheme_path)
parser.add_argument('output',
                    action='store',
                    type=Path,
                    help='The output directory')
parser.add_argument('input',
                    action='store',
                    nargs='+',
                    type=Path,
                    help='One or multiple input files or directories')
