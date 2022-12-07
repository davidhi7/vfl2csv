import io
import os
import sys
import logging
from pathlib import Path
from multiprocessing import Pool, get_context
import numpy as np

import openpyxl

from TrialSiteSheet import TrialSiteSheet

SHEETS_PER_PROCESS = 32

logging.basicConfig(format='%(levelname)s %(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def worksheet_pipeline(sheet_batch, workbook, in_mem_file, output_dir, process_index):
    logger = logging.getLogger(str(process_index))
    for sheet_name in sheet_batch:
        logger.info(f'Converting sheet {sheet_name}...')
        trialSiteSheet = TrialSiteSheet(workbook, in_mem_file, sheet_name)
        # trial_site_folder = Path(trialSiteSheet.replace_metadata_keys(str(output_dir / '{versuch}_{teilfläche}')))
        trial_site_folder = Path(output_dir / sheet_name)
        os.makedirs(trial_site_folder, exist_ok=True)
        trialSiteSheet.write_data(trial_site_folder / 'data.csv')
        trialSiteSheet.write_metadata(trial_site_folder / 'metadata.txt')


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
    with get_context('fork').Pool(processes=os.cpu_count()) as pool:
        process_args = zip(
            np.array_split(sheet_names, process_count),
            process_count * [workbook],
            process_count * [in_mem_file],
            process_count * [output_dir],
            range(process_count)
        )
        pool.starmap(worksheet_pipeline, process_args)

    logger.info('done')
