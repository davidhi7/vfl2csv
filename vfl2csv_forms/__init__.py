from pathlib import Path

from vfl2csv_base import (
    config_factory,
    default_column_scheme_path,
    default_column_scheme_json,
)
from vfl2csv_base.ColumnScheme import ColumnScheme

config = config_factory.get_config(
    Path("config/config_forms.ini"),
    """[Input]
metadata_search_pattern = *.txt
directory_search_recursively = true

[Output]
excel_sheet_pattern = {versuch}-{parzelle}
""",
)
column_scheme = ColumnScheme.from_file(
    path=default_column_scheme_path, template=default_column_scheme_json
)
