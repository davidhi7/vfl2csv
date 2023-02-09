import pathlib
from argparse import ArgumentParser

from vfl2csv_base import ColumnScheme

parser = ArgumentParser(
    prog='vfl2csv',
    description='Convert Versuchsflächendatenbanksystem-output into CSV files.'
)
parser.add_argument('--column-scheme', '-c',
                    action='store',
                    type=ColumnScheme.from_file,
                    help='Path to the column scheme configuration',
                    default='./config/columns.json')
parser.add_argument('output',
                    action='store',
                    type=pathlib.Path,
                    help='The output directory')
parser.add_argument('input',
                    action='store',
                    nargs='+',
                    type=pathlib.Path,
                    help='One or multiple input files or directories')
