import io
import logging
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import openpyxl

import TrialSiteSheet

SHEETS_PER_PROCESS = 32

logging.basicConfig(format='%(levelname)s %(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        logger.error('Not enough parameter provided. Input file and output directory are required!')
        exit(1)
    input_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    if not input_file.is_file():
        logger.error(f'{str(input_file)} is not a valid file!')
        exit(1)

    # read file into memory to not have to load the file repeatedly with openpyxl and pandas
    with open(input_file, 'rb') as file:
        in_mem_file = io.BytesIO(file.read())

    # find all sheets of the Excel file
    workbook = openpyxl.load_workbook(in_mem_file)
    sheet_names = workbook.sheetnames
    logger.info(f'Found {len(sheet_names)} trial sites within the Excel file')

    # use multiprocessing for improved performance
    process_count = max(round(len(sheet_names) / SHEETS_PER_PROCESS), 1)
    logger.info(f'Found {os.cpu_count()} CPU threads, {process_count} processes will be used')
    with Pool(processes=os.cpu_count()) as pool:
        process_args = zip(
            np.array_split(sheet_names, process_count),
            process_count * [workbook],
            process_count * [in_mem_file],
            process_count * [output_dir],
            range(process_count)
        )
        pool.starmap(TrialSiteSheet.worksheet_pipeline, process_args)

    logger.info('done')
