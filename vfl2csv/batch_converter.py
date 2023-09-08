import logging
import multiprocessing
import traceback
from collections import Counter
from configparser import ConfigParser
from multiprocessing import RLock, Pool
from pathlib import Path
from typing import TypedDict, Optional, Callable

import numpy as np

import vfl2csv
from tests.ConversionAuditor import ConversionAuditor
from vfl2csv import setup
from vfl2csv.exceptions import VerificationException
from vfl2csv.input.ExcelInputSheet import ExcelInputSheet
from vfl2csv.input.InputData import InputData
from vfl2csv.input.TsvInputFile import TsvInputFile
from vfl2csv.output.TrialSiteConverter import TrialSiteConverter
from vfl2csv_base.ColumnScheme import ColumnScheme
from vfl2csv_base.exceptions.IOErrors import FileSavingError

CONFIG_ALLOWED_INPUT_FORMATS = ('TSV', 'Excel')
logger = logging.getLogger(__name__)


class Report(TypedDict):
    total_count: int
    exceptions: list[Exception]
    metadata_output_files: list[Path]


def find_input_data(input_path: str | Path | list[str | Path]) -> tuple[list[Path], list[InputData]]:
    """
    Query input data recursively
    @param input_path: path string, Path object or list of path strings or Objects
    @return: List of input files, list of InputData objects
    """
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


# noinspection PyBroadException
def trial_site_pipeline(
        config: ConfigParser,
        column_scheme: ColumnScheme,
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
    @param column_scheme: Column scheme to work with
    @param config: Configuration to work with
    @param input_batch: List of `InputData` objects
    @param output_data_pattern: Pattern for storing data files
    @param output_metadata_pattern: Pattern for storing metadata files
    @param lock: Lock for synchronization
    @param on_progress: Callable to execute after finishing a trial site conversion.
    Consumes a string summarizing the input file.
    @param on_progress_queue: Similar to `on_progress`, a string representation of a trial site is put into the
    multiprocessing queue after finishing its conversion.
    @param process_index: Index of the current process for logging. If multiprocessing is not used, the parameter can be
    omitted.
    @return: report of all conversions containing metadata and exceptions.
    """
    vfl2csv.setup.config = config
    vfl2csv.setup.column_scheme = column_scheme
    process_logger = logging.getLogger(f'process {process_index}' if process_index is not None else __name__)
    # store all metadata output files to check for exceptions later
    metadata_output_files = []
    errors = []
    for input_data in input_batch:
        try:

            process_logger.info(f'Converting input {str(input_data)}')
            trial_site = input_data.parse()
            converter = TrialSiteConverter(trial_site, input_data.file_path)
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

            try:
                converter.write_data(data_output_file)
            except OSError as error:
                raise FileSavingError(data_output_file) from error
            try:
                converter.write_metadata(metadata_output_file)
            except OSError as error:
                raise FileSavingError(metadata_output_file) from error

            metadata_output_files.append(metadata_output_file)
        except Exception as exc:
            errors.append(exc)
            process_logger.exception(f'Failed conversion for trial site `{input_data.string_representation()}`')
        finally:
            if on_progress is not None:
                on_progress(str(input_data))
            if on_progress_queue is not None:
                on_progress_queue.put(str(input_data))
    return {
        'total_count': len(input_batch),
        'exceptions': errors,
        'metadata_output_files': metadata_output_files
    }


def run(output_dir: Path, input_path: str | Path | list[str | Path],
        on_progress: Optional[Callable[[Optional[str]], None]]) -> Report:
    """
    Convert vfl files to CSV and metadata files.
    If exceptions occur during the conversion process, a ConversionException is raised.
    If the verification of converted files fails or reports issues, a VerificationException is raised.
    :param output_dir: Output directory
    :param input_path: List of file or directories to search for input files. See batch_converter.find_input_data()
    :param on_progress: Optional callback that is invoked after every converted trial site
    :return: Report of the conversion process
    """
    input_files, input_trial_sites = find_input_data(input_path)
    logger.info(f'Found {len(input_trial_sites)} trial sites in {len(input_files)} '
                f'{setup.config["Input"]["input_format"]} files')

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
                # Passing on_progress callbacks to different processes may cause issues depending on the callback.
                # Therefore, we invoke the callbacks in the main process while communicating with the other processes
                # using a queue
                process_args = zip(
                    process_count * [vfl2csv.setup.config],
                    process_count * [vfl2csv.setup.column_scheme],
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
                    # Run `on_progress` for every expected value of the queue after finishing all batches
                    expected_queue_values = len(input_trial_sites)
                    # count of values received from the queue
                    received_queue_values = 0

                    # Run until either all processes are finished or the count of received queue values matches the
                    # count of input trial sites
                    while not result.ready() and received_queue_values < expected_queue_values:
                        value = queue.get()
                        if value is None:
                            break
                        on_progress(value)
                        received_queue_values += 1
                else:
                    # If there is no on_progress callback, simply wait for the processes to finish
                    result.wait()
                summarised_result: Report = Counter()
                for r in result.get():
                    # noinspection PyTypeChecker
                    summarised_result.update(r)
    else:
        # allow disabling multiprocessing for easier debugging and optimized performance when working with little data
        logger.info('Multiprocessing is disabled')
        summarised_result: Report = trial_site_pipeline(
            vfl2csv.setup.config,
            vfl2csv.setup.column_scheme,
            input_trial_sites,
            output_data_file,
            output_metadata_file,
            RLock(),
            on_progress=on_progress,
            on_progress_queue=None,
            process_index=0
        )
    summarised_result: Report = dict(summarised_result)

    if len(summarised_result['exceptions']) != 0:
        message = f'{len(summarised_result["exceptions"])} exceptions occurred during converting ' \
                  f'{summarised_result["total_count"]} trial sites'
        logger.warning(message)
        raise ExceptionGroup(message, summarised_result['exceptions'])

    logger.info(
        f'Converted {summarised_result["total_count"]} trial sites successfully, proceed with verification of '
        f'converted trial sites.')

    try:
        auditor = ConversionAuditor(vfl2csv_config=setup.config, column_scheme=setup.column_scheme)
        auditor.set_reference_files(input_files)
        auditor.audit_converted_metadata_files(summarised_result['metadata_output_files'])
        logger.info('Verification succeeded')
        return summarised_result
    except ValueError as exception:
        logger.error(f'Verification failed: {exception}')
        logger.error(traceback.format_exc())
        raise VerificationException(exception)
