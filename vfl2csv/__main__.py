import argparse
import logging
import pathlib

from vfl2csv import batch_converter

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
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
    arguments = vars(parser.parse_args())
    batch_converter.run(arguments['output'], arguments['input'])
