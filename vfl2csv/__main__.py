import io
import os
import sys
import logging
from pathlib import Path

import openpyxl

from TrialSiteSheet import TrialSiteSheet

logging.basicConfig(format='%(levelname)s %(module)s: %(message)s', level=logging.INFO)
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

    for sheet_name in sheet_names:
        logger.info(f'Converting sheet {sheet_name}...')
        trialSiteSheet = TrialSiteSheet(workbook, in_mem_file, sheet_name)
        trial_site_folder = Path(trialSiteSheet.replace_metadata_keys(str(output_dir / '{versuch}_{teilfläche}')))
        os.makedirs(trial_site_folder, exist_ok=True)
        trialSiteSheet.write_data(trial_site_folder / 'data.csv')
        trialSiteSheet.write_metadata(trial_site_folder / 'metadata.txt')

    print('done')
