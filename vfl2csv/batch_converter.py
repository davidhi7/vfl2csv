import logging
import multiprocessing
import traceback
from collections import Counter
from multiprocessing import RLock, Pool
from pathlib import Path

import numpy as np

from vfl2csv import config
from vfl2csv.input.ExcelInputSheet import ExcelInputSheet
from vfl2csv.input.InputFile import InputFile
from vfl2csv.input.TsvInputFile import TsvInputFile
from vfl2csv.output.TrialSiteConverter import TrialSiteConverter

CONFIG_ALLOWED_INPUT_FORMATS = ('TSV', 'Excel')
logger = logging.getLogger(__name__)


def validate(argv):
    if config["Input"]["input_format"] not in CONFIG_ALLOWED_INPUT_FORMATS:
        raise ValueError(
            f'{config["Input"]["input_format"]} is not a valid output format. Allowed formats are {", ".join(CONFIG_ALLOWED_INPUT_FORMATS)}!')
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
) -> dict[str, int]:
    logger = logging.getLogger(f'process {process_index}')
    errors = list()
    for input_sheet in input_batch:
        # noinspection PyBroadException
        try:
            logger.info(f'Converting input {str(input_sheet)}')
            input_sheet.parse()
            trial_site = input_sheet.get_trial_site()
            converter = TrialSiteConverter(trial_site)
            converter.refactor_dataframe()
            converter.refactor_metadata()

            data_output_file = trial_site.replace_metadata_keys(output_data_pattern)
            metadata_output_file = trial_site.replace_metadata_keys(output_metadata_pattern)
            converter.trial_site.metadata['DataFrame'] = str(
                data_output_file.absolute().relative_to(metadata_output_file.parent.absolute()))

            data_output_file.parent.mkdir(parents=True, exist_ok=True)
            metadata_output_file.parent.mkdir(parents=True, exist_ok=True)

            # lock this segment to prevent race conditions during multiprocessing.
            with lock:
                try:
                    data_output_file.touch(exist_ok=False)
                    metadata_output_file.touch(exist_ok=False)
                except FileExistsError as e:
                    raise Exception(
                        f'Process {process_index}: Corresponding output file(s) for trial site {input_sheet} does already exist!') from e

            converter.write_data(data_output_file)
            converter.write_metadata(metadata_output_file)
        except Exception as e:
            traceback.print_exc();
            logger.warning(f'Exception in process {process_index}: {str(e)}')
            errors.append(e)
    return {
        'total_count': len(input_batch),
        'errors': len(errors)
    }


def run(argv):
    try:
        validate(argv)
    except ValueError as e:
        logger.error('Validation failed: ' + str(e))
        exit(1)
    input_path = Path(argv[1])
    output_dir = Path(argv[2])
    input_files, input_trial_sites = find_input_sheets(input_path)
    logger.info(
        f'Found {len(input_trial_sites)} trial sites in {len(input_files)} {config["Input"]["input_format"]} files')

    output_data_file = output_dir / config['Output'].getpath('csv_output_pattern')
    output_metadata_file = output_dir / config['Output'].getpath('metadata_output_pattern')
    logger.info(f'Writing output to {output_dir}')

    process_count = max(round(len(input_trial_sites) / config['Multiprocessing'].getint('sheets_per_core', 32)), 1)
    if config['Multiprocessing'].getboolean('enabled', False) and process_count > 1:
        # use multiprocessing for improved performance with larger inputs
        logger.info(f'Found {multiprocessing.cpu_count()} CPU threads, {process_count} processes are going to be used')

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
                result = pool.starmap(trial_site_pipeline, process_args)
                summarised_result = Counter()
                for r in result:
                    summarised_result.update(r)
    else:
        # allow disabling multiprocessing for easier debugging and optimized performance when working with little data
        logger.info('Multiprocessing is disabled')
        summarised_result = trial_site_pipeline(input_trial_sites, output_data_file, output_metadata_file, lock=RLock(),
                                                process_index=0)

    logger.info(
        f'Converted {summarised_result["total_count"]} trial sites, {summarised_result["errors"]} errors occured.')
