import configparser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from vfl2csv_base import config_factory, default_column_scheme_json, default_column_scheme_path
from vfl2csv_base.ColumnScheme import ColumnScheme

default_config = """[Input]
# TSV for tab delimited values or Excel for Excel files
input_format = Excel
input_file_extension = xlsx
# expect python codec name (https://docs.python.org/3/library/codecs.html#standard-encodings)
tsv_encoding = iso8859_15
directory_search_recursively = true

[Output]
metadata_output_pattern = {revier}/{versuch}/{versuch}-{parzelle}_metadata.txt
# csv output pattern directory must be same or sub directory of metadata path
csv_output_pattern = {revier}/{versuch}/{versuch}-{parzelle}.csv

[Multiprocessing]
enabled = true
sheets_per_core = 32
"""


@dataclass
class Setup:
    config: configparser.ConfigParser
    column_scheme: ColumnScheme


setup = Setup(config=config_factory.get_config('./config/config_vfl2csv.ini'),
              column_scheme=ColumnScheme.from_file(default_column_scheme_path))


def set_custom_configs(config_path: Optional[Path], column_scheme_path: Optional[Path]):
    if config_path is not None:
        setup.config = config_factory.get_config(config_path, template=default_config)
    if column_scheme_path is not None:
        setup.column_scheme = ColumnScheme.from_file(column_scheme_path, template=default_column_scheme_json)
