import logging
import sys
from pathlib import Path

from vfl2csv_base.config_factory import get_config

if 'unittest' in sys.modules:
    logging.basicConfig(format='%(levelname)s %(name)s: %(message)s', level=logging.WARNING)
else:
    logging.basicConfig(format='%(levelname)s %(name)s: %(message)s', level=logging.INFO)

test_config = get_config(Path('tests/test-config.ini'))

default_column_scheme_json = """{
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
"""
default_column_scheme_path = Path('./config/columns.json')
