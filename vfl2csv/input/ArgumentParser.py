from argparse import ArgumentParser
import pathlib

parser = ArgumentParser(
    prog='vfl2csv',
    description='Convert Versuchsflächendatenbanksystem-output into CSV files.'
)
parser.add_argument('output',
                    action='store',
                    type=pathlib.Path,
                    help='The output directory')
parser.add_argument('input',
                    action='store',
                    nargs='+',
                    type=pathlib.Path,
                    help='One or multiple input files or directories')
