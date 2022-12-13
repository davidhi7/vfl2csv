import logging
import configparser
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import TrialSiteConverter
from input.ExcelInputSheet import ExcelInputSheet
from ExcelWorkbook import ExcelWorkbook
from input.TsvInputFile import TSVInputFile

config = configparser.ConfigParser(converters={'path': Path})
config.read('config.ini')
config_allowed_input_formats = ('TSV', 'Excel')

logging.basicConfig(format='%(levelname)s %(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # input validation
    if config["Input"]["input_format"] not in config_allowed_input_formats:
        logger.error(
            f'{config["Input"]["input_format"]} is not a valid input format.'
            f'Allowed formats are {", ".join(config_allowed_input_formats)}!'
        )
        exit(1)
    if len(sys.argv) < 3:
        logger.error('Not enough parameter provided. Input file and output directory are required!')
        exit(1)
    input_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    if not input_path.exists():
        logger.error(f'{str(input_path)} must be a file or folder!')
        exit(1)
    if input_path.is_file():
        input_files = (input_path,)
    else:
        input_files = tuple(input_path.glob(f'*.{config["Input"]["input_file_extension"]}'))
    output_data_file = output_dir / config['Output'].getpath('csv_output_pattern')
    output_metadata_file = output_dir / config['Output'].getpath('metadata_output_pattern')

    # managing input files
    if config["Input"]["input_format"] == 'Excel':
        excel_workbooks = list(ExcelWorkbook(path) for path in input_files)
        input_trial_sites = ExcelInputSheet.iterate_sheets(excel_workbooks)
        logger.info(f'Found {len(input_trial_sites)} trial sites in {len(excel_workbooks)} Excel files')
    else:
        input_trial_sites = [TSVInputFile(path) for path in input_files]
        logger.info(f'Found {len(input_trial_sites)} tab-delimited trial site files')

    # processing input files
    logger.info(f'Writing output to {output_dir}')
    if config['Multiprocessing'].getboolean('enabled', False):
        # use multiprocessing for improved performance with larger inputs
        process_count = max(round(len(input_trial_sites) / config['Multiprocessing'].getint('sheets_per_core', 32)), 1)
        logger.info(f'Found {os.cpu_count()} CPU threads, {process_count} processes will be used')
        with Pool(processes=os.cpu_count()) as pool:
            process_args = zip(
                np.array_split(input_trial_sites, process_count),
                process_count * [output_data_file],
                process_count * [output_metadata_file],
                range(process_count)
            )
            pool.starmap(TrialSiteConverter.trial_site_pipeline, process_args)
    else:
        # allow disabling multiprocessing for easier debugging
        logger.info('Multiprocesing is disabled')
        TrialSiteConverter.trial_site_pipeline(input_trial_sites, output_data_file, output_metadata_file, 0)

    logger.info('done')
