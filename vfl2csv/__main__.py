import logging

from vfl2csv import arguments
from vfl2csv.batch_converter import run

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    run(arguments['output'], arguments['input'])
