import logging
import sys

import vfl2csv
from vfl2csv.ArgumentParser import parser
from vfl2csv.batch_converter import run

logger = logging.getLogger(__name__)


def start(args):
    arguments = vars(parser.parse_args(args))
    if 'config' in arguments or 'column_scheme' in arguments:
        vfl2csv.set_custom_configs(config_path=arguments['config'], column_scheme_path=arguments['column_scheme'])
    success, report = run(arguments['output'], arguments['input'], None)
    if not success:
        logger.info('Failed')
        return 1

    logger.info('Done')
    return 0


if __name__ == '__main__':
    sys.exit(start(sys.argv[1:]))
