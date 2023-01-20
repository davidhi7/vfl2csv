import logging
import sys
from pathlib import Path
import time
import tempfile
import shutil

import pandas as pd

from vfl2csv_forms.InputHandler import InputHandler

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    input_path = Path(sys.argv[1])
    if not (input_path.is_dir() or input_path.is_file()):
        logger.error('First must be a input file or directory!')
        sys.exit(1)

    temp_dir = Path(tempfile.mkdtemp())

    times = []
    # do 100 iterations
    for i in range(100):
        time0 = time.time()
        input_handler = InputHandler()
        input_handler.load_input(input_path)
        for _ in input_handler.create_all(output_file=temp_dir / f'form_{i}.xlsx'):
            ...
        time1 = time.time()
        times.append((time1 - time0))

    shutil.rmtree(temp_dir)
    times_series = pd.Series(times)
    logger.info('benchmark results (s): \n' + str(times_series.describe()))
