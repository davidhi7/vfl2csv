import sys

from vfl2csv.ArgumentParser import parser
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

if 'unittest' in sys.modules or 'vfl2csv_gui' in sys.modules:
    config = config_factory.get_config('./config/config_vfl2csv.ini')
    column_scheme = ColumnScheme.from_file(default_column_scheme_path)
else:
    arguments = vars(parser.parse_args())
    config = config_factory.get_config(arguments['config'], template=default_config)
    column_scheme = ColumnScheme.from_file(arguments['column_scheme'], template=default_column_scheme_json)
