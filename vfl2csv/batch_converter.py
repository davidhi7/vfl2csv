import logging
import multiprocessing
import traceback
from collections import Counter
from multiprocessing import RLock, Pool
from pathlib import Path

import numpy as np

from tests.ConversionAuditor import ConversionAuditor
from vfl2csv import column_scheme
from vfl2csv import config
from vfl2csv.input.ExcelInputSheet import ExcelInputSheet
from vfl2csv.input.InputData import InputData
from vfl2csv.input.TsvInputFile import TsvInputFile
from vfl2csv.output.TrialSiteConverter import TrialSiteConverter

CONFIG_ALLOWED_INPUT_FORMATS = ('TSV', 'Excel')
logger = logging.getLogger(__name__)


def find_input_data(input_path: str | Path | list[str | Path]) -> tuple[list[Path], list[InputData]]:
    # if `input_path` is a string, convert to a path
    if isinstance(input_path, str):
        input_path = Path(input_path)

    # if `input_path` is a list, find recursively
    if not isinstance(input_path, Path):
        accumulated_input_files = []
        accumulated_input_trial_sites = []

        for path in input_path:
            input_files, input_data = find_input_data(path)
            accumulated_input_files.extend(input_files)
            accumulated_input_trial_sites.extend(input_data)
        return accumulated_input_files, accumulated_input_trial_sites

    if input_path.is_file():
        input_files = (input_path,)
    else:
        input_file_extension = config['Input']['input_file_extension']
        if config['Input'].getboolean('directory_search_recursively', False):
            input_files = list(input_path.rglob(f'*.{input_file_extension}'))
        else:
            input_files = list(input_path.glob(f'*.{input_file_extension}'))

    if config['Input']['input_format'] == 'Excel':
        input_data = ExcelInputSheet.iterate_files(input_files)
    elif config['Input']['input_format'] == 'TSV':
        input_data = TsvInputFile.iterate_files(input_files)
    else:
        raise ValueError(f'Input format {config["Input"]["input_format"]} is neither "Excel" nor "TSV"')

    return input_files, input_data


def trial_site_pipeline(
        input_batch: list[InputData],
        output_data_pattern: Path,
        output_metadata_pattern: Path,
        lock: RLock,
        process_index: int
) -> dict[str, int]:
    process_logger = logging.getLogger(f'process {process_index}')
    # store all metadata output files to check for errors later
    metadata_output_files = []
    errors = []
    for input_data in input_batch:
        # noinspection PyBroadException
        try:
            process_logger.info(f'Converting input {str(input_data)}')
            trial_site = input_data.parse()
            converter = TrialSiteConverter(trial_site)
            converter.refactor_dataframe()
            converter.trim_metadata()

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
                        f'Process {process_index}: Corresponding output file(s) for trial site {input_data} does '
                        f'already exist!') from e

            converter.write_data(data_output_file)
            converter.write_metadata(metadata_output_file)

            metadata_output_files.append(metadata_output_file)
        except Exception as e:
            traceback.print_exc()
            process_logger.warning(f'Exception in process {process_index}: {str(e)}')
            errors.append(e)
    return {
        'total_count': len(input_batch),
        'errors': len(errors),
        'metadata_output_files': metadata_output_files
    }


def run(output_dir: Path, input_path: list[Path]) -> int:
    input_files, input_trial_sites = find_input_data(input_path)
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
        summarised_result = trial_site_pipeline(input_trial_sites,
                                                output_data_file,
                                                output_metadata_file,
                                                RLock(),
                                                process_index=0
                                                )

    logger.info(
        f'Converted {summarised_result["total_count"]} trial sites, {summarised_result["errors"]} errors occurred.')

    if summarised_result["errors"] > 0:
        logger.error(
            f'Converted {summarised_result["total_count"]} trial sites, {summarised_result["errors"]} errors occurred.'
            f'\nSkip checks due to the errors'
        )
        return 1

    logger.info(f'Converted {summarised_result["total_count"]} trial sites without errors.')

    # Verify converted files
    logger.info('Verify all output files...')
    auditor = ConversionAuditor(vfl2csv_config=config, column_scheme=column_scheme)
    auditor.set_reference_files(input_files)
    # `summarised_result['metadata_output_files']` returns a list of all metadata output file paths, not an int
    # noinspection PyTypeChecker
    auditor.audit_converted_metadata_files(summarised_result['metadata_output_files'])
    logger.info('Verification completed, no errors')
    return 0
