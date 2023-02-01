import argparse
import logging
import pathlib

from vfl2csv import batch_converter
from vfl2csv.input.ArgumentParser import parser

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    arguments = vars(parser.parse_args())
    batch_converter.run(arguments['output'], arguments['input'])
