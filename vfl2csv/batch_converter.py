import logging
import multiprocessing
import traceback
from collections import Counter
from multiprocessing import RLock, Pool
from pathlib import Path
from typing import TypedDict, Optional, Callable

import numpy as np

from tests.ConversionAuditor import ConversionAuditor
from vfl2csv import setup
from vfl2csv.input.ExcelInputSheet import ExcelInputSheet
from vfl2csv.input.InputData import InputData
from vfl2csv.input.TsvInputFile import TsvInputFile
from vfl2csv.output.TrialSiteConverter import TrialSiteConverter
from vfl2csv_gui.interfaces.ExceptionReport import ExceptionReport

CONFIG_ALLOWED_INPUT_FORMATS = ('TSV', 'Excel')
logger = logging.getLogger(__name__)


class Report(TypedDict, total=False):
    total_count: int
    errors: list[ExceptionReport]
    metadata_output_files: list[Path]
    verification_success: Optional[bool]
    verification_error: Optional[ExceptionReport]


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
        input_file_extension = setup.config['Input']['input_file_extension']
        if setup.config['Input'].getboolean('directory_search_recursively', False):
            input_files = list(input_path.rglob(f'*.{input_file_extension}'))
        else:
            input_files = list(input_path.glob(f'*.{input_file_extension}'))

    if setup.config['Input']['input_format'] == 'Excel':
        input_data = ExcelInputSheet.iterate_files(input_files)
    elif setup.config['Input']['input_format'] == 'TSV':
        input_data = TsvInputFile.iterate_files(input_files)
    else:
        raise ValueError(f'Input format {setup.config["Input"]["input_format"]} is neither "Excel" nor "TSV"')

    return input_files, input_data


def trial_site_pipeline(
        input_batch: list[InputData],
        output_data_pattern: Path,
        output_metadata_pattern: Path,
        lock: RLock,
        on_progress: Optional[Callable[[str | None], None]],
        on_progress_queue: Optional[multiprocessing.Queue],
        process_index: Optional[int]
) -> Report:
    """
    Convert a batch of input data.
    @param input_batch: List of `InputData` objects
    @param output_data_pattern: Pattern for storing data files
    @param output_metadata_pattern: Pattern for storing metadata files
    @param lock: Lock for synchronization
    @param on_progress: Callable to execute after finishing a trial site conversion.
    Consumes a string summarizing the input file.
    @param on_progress_queue: Similar to `on_progress`, a string representation of a trial siteis put into the queue
    after finishing its conversion.
    @param process_index: Index of the current process for logging. If multiprocessing is not used, the parameter can be
    omitted.
    @return: report of all conversions containing metadata and errors.
    """
    process_logger = logging.getLogger(f'process {process_index if process_index is not None else "root"}')
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
                data_output_file.touch(exist_ok=False)
                metadata_output_file.touch(exist_ok=False)

            converter.write_data(data_output_file)
            converter.write_metadata(metadata_output_file)

            metadata_output_files.append(metadata_output_file)
        except Exception as exc:
            exc_traceback = traceback.format_exc()
            process_logger.warning(f'Exception in process {process_index}: {str(exc)}\n{exc_traceback}')
            errors.append(ExceptionReport(exc, exc_traceback))
        finally:
            if on_progress is not None:
                on_progress(str(input_data))
            if on_progress_queue is not None:
                on_progress_queue.put(str(input_data))
    return {
        'total_count': len(input_batch),
        'errors': errors,
        'metadata_output_files': metadata_output_files
    }


def run(output_dir: Path, input_path: list[Path], on_progress: Optional[Callable[[Optional[str]], None]]) -> tuple[
    bool, Report]:
    input_files, input_trial_sites = find_input_data(input_path)
    logger.info(
        f'Found {len(input_trial_sites)} trial sites in {len(input_files)} {setup.config["Input"]["input_format"]} files')

    output_data_file = output_dir / setup.config['Output'].getpath('csv_output_pattern')
    output_metadata_file = output_dir / setup.config['Output'].getpath('metadata_output_pattern')
    logger.info(f'Writing output to {output_dir}')

    process_count = max(round(len(input_trial_sites) / setup.config['Multiprocessing'].getint('sheets_per_core', 32)),
                        1)
    if setup.config['Multiprocessing'].getboolean('enabled', False) and process_count > 1:
        # use multiprocessing for improved performance with larger inputs
        logger.info(f'Found {multiprocessing.cpu_count()} CPU threads, {process_count} processes are going to be used')

        with multiprocessing.Manager() as manager:
            lock = manager.RLock()
            queue = manager.Queue()
            with Pool() as pool:
                process_args = zip(
                    np.array_split(input_trial_sites, process_count),
                    process_count * [output_data_file],
                    process_count * [output_metadata_file],
                    process_count * [lock],
                    process_count * [None],
                    process_count * [queue],
                    range(process_count)
                )
                result = pool.starmap_async(trial_site_pipeline, process_args)

                if on_progress is not None:
                    expected_queue_values = len(input_trial_sites)
                    actual_queue_values = 0

                    while not result.ready() and actual_queue_values < expected_queue_values:
                        value = queue.get()
                        if value is None:
                            break
                        on_progress(value)
                        actual_queue_values += 1
                else:
                    result.wait()
                summarised_result: Report = Counter()
                for r in result.get():
                    summarised_result.update(r)
    else:
        # allow disabling multiprocessing for easier debugging and optimized performance when working with little data
        logger.info('Multiprocessing is disabled')
        summarised_result: Report = trial_site_pipeline(input_trial_sites,
                                                        output_data_file,
                                                        output_metadata_file,
                                                        RLock(),
                                                        on_progress=on_progress,
                                                        on_progress_queue=None,
                                                        process_index=0)
    summarised_result: Report = dict(summarised_result)

    if len(summarised_result['errors']) != 0:
        logger.warning(
            f'{len(summarised_result["errors"])} errors occurred during converting {summarised_result["total_count"]} '
            f'trial sites')
        return False, summarised_result

    logger.info(
        f'Converted {summarised_result["total_count"]} trial sites successfully, proceed with verification of '
        f'converted trial sites.')

    try:
        auditor = ConversionAuditor(vfl2csv_config=setup.config, column_scheme=setup.column_scheme)
        auditor.set_reference_files(input_files)
        auditor.audit_converted_metadata_files(summarised_result['metadata_output_files'])
        summarised_result['verification_success'] = True
        logger.info('Verification succeeded')
    except ValueError as exc:
        exc_traceback = traceback.format_exc()
        logger.error(f'Verification failed: {exc}')
        summarised_result['verification_error'] = ExceptionReport(exc, exc_traceback)
        summarised_result['verification_success'] = False

    success = len(summarised_result['errors']) == 0 \
              and summarised_result.get('verification_success') is True \
              and summarised_result.get('verification_error') is None
    return success, summarised_result
