from pathlib import Path

from vfl2csv_base import config_factory

config = config_factory.get_config(Path('config/config_forms.ini'), """[Input]
metadata_search_pattern = *.txt
directory_search_recursively = true

[Output]
excel_sheet_pattern = {versuch}-{parzelle}
""")
