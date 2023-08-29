import logging
import sys
import traceback

import vfl2csv
from vfl2csv.ArgumentParser import parser
from vfl2csv.batch_converter import run
from vfl2csv.exceptions import VerificationException, ConversionException

logger = logging.getLogger(__name__)


def start(args):
    arguments = vars(parser.parse_args(args))
    if 'config' in arguments or 'column_scheme' in arguments:
        vfl2csv.set_custom_configs(config_path=arguments['config'], column_scheme_path=arguments['column_scheme'])
    try:
        run(arguments['output'], arguments['input'], on_progress=None)
    except (ConversionException, VerificationException) as _:
        logger.warning('Failed to convert files')
        logger.warning(traceback.format_exc())
        return 1

    logger.info('Done')
    return 0


if __name__ == '__main__':
    sys.exit(start(sys.argv[1:]))
