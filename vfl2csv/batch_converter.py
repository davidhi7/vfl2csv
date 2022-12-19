import logging
import multiprocessing
from multiprocessing import RLock, Pool
from pathlib import Path

import numpy as np

from config import config
from input.ExcelInputSheet import ExcelInputSheet
from input.InputFile import InputFile
from input.TsvInputFile import TsvInputFile

CONFIG_ALLOWED_INPUT_FORMATS = ('TSV', 'Excel')
logger = logging.getLogger(__name__)


def validate(argv):
    if config["Input"]["input_format"] not in CONFIG_ALLOWED_INPUT_FORMATS:
        raise ValueError(
            f'{config["Input"]["input_format"]} is not a valid input format. Allowed formats are {", ".join(CONFIG_ALLOWED_INPUT_FORMATS)}!')
    if len(argv) < 3:
        raise ValueError(
            'Invalid number of arguments provided. Input file or directory and output directory are required!')
    if not Path(argv[1]).exists():
        raise ValueError(f'{str(argv[1])} must be a file or folder!')
    return


def find_input_sheets(input_path: Path) -> tuple[list[Path], list[InputFile]]:
    if input_path.is_file():
        input_files = (input_path,)
    else:
        input_files = list(input_path.glob(f'*.{config["Input"]["input_file_extension"]}'))

    if config["Input"]["input_format"] == 'Excel':
        input_trial_sites = ExcelInputSheet.iterate_files(input_files)
    else:
        input_trial_sites = TsvInputFile.iterate_files(input_files)

    return input_files, input_trial_sites


def trial_site_pipeline(
        input_batch: list[InputFile],
        output_data_pattern: Path,
        output_metadata_pattern: Path,
        lock: RLock,
        process_index: int
) -> None:
    logger = logging.getLogger(f'process {process_index}')
    for input_sheet in input_batch:
        logger.info(f'Converting input {str(input_sheet)}')
        input_sheet.parse()
        trial_site = input_sheet.get_trial_site()
        trial_site.refactor_dataframe()

        data_output_file = trial_site.replace_metadata_keys(output_data_pattern)
        metadata_output_file = trial_site.replace_metadata_keys(output_metadata_pattern)

        data_output_file.parent.mkdir(parents=True, exist_ok=True)
        metadata_output_file.parent.mkdir(parents=True, exist_ok=True)

        # lock this segment to prevent race conditions during multiprocessing.
        # If lock is None, it is assumed that no multiprocessing is used.
        if lock is not None:
            with lock:
                try:
                    data_output_file.touch(exist_ok=False)
                    metadata_output_file.touch(exist_ok=False)
                except FileExistsError as err:
                    raise Exception(
                        f'Process {process_index}: Corresponding output file(s) for trial site {input_sheet} does already exist!') from err

        trial_site.write_data(data_output_file)
        trial_site.write_metadata(metadata_output_file)


def run(argv):
    try:
        validate(argv)
    except ValueError as e:
        print('Validation failed:', e)
        exit(1)
    input_path = Path(argv[1])
    output_dir = Path(argv[2])
    input_files, input_trial_sites = find_input_sheets(input_path)
    logger.info(
        f'Found {len(input_trial_sites)} trial sites in {len(input_files)} {config["Input"]["input_format"]} files')

    output_data_file = output_dir / config['Output'].getpath('csv_output_pattern')
    output_metadata_file = output_dir / config['Output'].getpath('metadata_output_pattern')
    logger.info(f'Writing output to {output_dir}')
    if config['Multiprocessing'].getboolean('enabled', False):
        # use multiprocessing for improved performance with larger inputs
        process_count = max(round(len(input_trial_sites) / config['Multiprocessing'].getint('sheets_per_core', 32)), 1)
        logger.info(f'Found {multiprocessing.cpu_count()} CPU threads, {process_count} processes will be used')

        with multiprocessing.Manager() as manager:
            lock = manager.RLock()
            with Pool() as pool:
                process_args = zip(
                    np.array_split(input_trial_sites, process_count),
                    process_count * [output_data_file],
                    process_count * [output_metadata_file],
                    process_count * [lock],
                    range(process_count)
                )
                pool.starmap(trial_site_pipeline, process_args)

    else:
        # allow disabling multiprocessing for easier debugging
        logger.info('Multiprocesing is disabled')
        trial_site_pipeline(input_trial_sites, output_data_file, output_metadata_file, lock=None, process_index=0)

    logger.info('done')
