import logging
import sys

from vfl2csv import arguments
from vfl2csv.batch_converter import run

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    success, report = run(arguments['output'], arguments['input'])
    if not success:
        logger.info('Failed')
        sys.exit(1)

    logger.info('Done')
    sys.exit(0)
