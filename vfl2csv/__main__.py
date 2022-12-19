import logging
import sys

from batch_converter import run

logging.basicConfig(format='%(levelname)s %(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    run(sys.argv)
