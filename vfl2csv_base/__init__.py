import logging
import sys
from pathlib import Path

if 'unittest' in sys.modules:
    logging.basicConfig(format='%(levelname)s %(name)s: %(message)s')
else:
    logging.basicConfig(format='%(levelname)s %(name)s: %(message)s')
    logging.disable(logging.WARNING)

from vfl2csv_base.ColumnScheme import ColumnScheme
from vfl2csv_base.config_factory import get_config

testconfig = get_config(Path('tests/test-config.ini'))
column_scheme = ColumnScheme.from_file(Path('config/columns.json'), """{
  "head": [
    {
      "override_name": "Bestandeseinheit",
      "form_include": false,
      "type": "uint16"
    },
    {
      "override_name": "Baumart",
      "type": "string"
    },
    {
      "override_name": "Baumnummer",
      "type": "uint32"
    }
  ],
  "measurements": [
    {
      "override_name": "D",
      "new_columns_count": 2,
      "add_difference": true,
      "type": "float64"
    },
    {
      "override_name": "Aus",
      "form_include": false,
      "type": "uint8"
    },
    {
      "override_name": "H",
      "type": "float64"
    }
  ]
}
""")
