import logging
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import TrialSiteSheet
from ExcelWorkbook import ExcelWorkbook
from ExcelWorksheet import ExcelWorksheet

SHEETS_PER_PROCESS = 32

logging.basicConfig(format='%(levelname)s %(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        logger.error('Not enough parameter provided. Input file and output directory are required!')
        exit(1)
    input_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    if not input_path.exists():
        logger.error(f'{str(input_path)} must be a file or folder!')
        exit(1)
    if input_path.is_file():
        input_files = (input_path, )
    else:
        input_files = tuple(input_path.glob('*.xlsx'))

    logger.info(f'Loading {len(input_files)} Excel files')
    excel_workbooks = list(ExcelWorkbook(path) for path in input_files)
    excel_worksheets = []
    for workbook in excel_workbooks:
        excel_worksheets.extend(ExcelWorksheet(workbook, sheet_name) for sheet_name in workbook.sheets)

    logger.info(f'Found {len(excel_worksheets)} trial sites in {len(excel_workbooks)} Excel files')

    # use multiprocessing for improved performance
    process_count = max(round(len(excel_worksheets) / SHEETS_PER_PROCESS), 1)
    logger.info(f'Found {os.cpu_count()} CPU threads, {process_count} processes will be used')
    with Pool(processes=os.cpu_count()) as pool:
        process_args = zip(
            np.array_split(excel_worksheets, process_count),
            process_count * [output_dir],
            range(process_count)
        )
        pool.starmap(TrialSiteSheet.worksheet_pipeline, process_args)

    logger.info('done')
