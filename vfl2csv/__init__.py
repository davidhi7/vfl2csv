from pathlib import Path

from vfl2csv_base import config_factory

config = config_factory.get_config(Path('config/config_vfl2csv.ini'), """[Input]
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
""")
