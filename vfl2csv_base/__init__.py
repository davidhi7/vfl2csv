import logging
import sys
from pathlib import Path

from vfl2csv_base.config_factory import get_config

if 'unittest' in sys.modules:
    logging.basicConfig(format='%(levelname)s %(name)s: %(message)s', level=logging.WARNING)
else:
    logging.basicConfig(format='%(levelname)s %(name)s: %(message)s', level=logging.INFO)

test_config = get_config(Path('config/config_tests.ini'))

default_column_scheme_json = """{"head":[{"name":"Bst.-E.","override_name":"Bestandeseinheit","form_include":false,"type":"uint16"},{"name":"Art","override_name":"Baumart","display_name":"BA","type":"string"},{"name":"Baum","override_name":"Baumnummer","display_name":"BNr","type":"uint32"}],"measurements":[{"name":"D","new_columns_count":2,"add_difference":true,"type":"float64"},{"name":"Typ","override_name":"Typ-D","form_include":false,"optional":true,"type":"uint8"},{"name":"MH","form_include":false,"optional":true,"type":"float64"},{"name":"Aus","form_include":false,"type":"uint8"},{"name":"NVP","form_include":false,"optional":true,"type":"uint16"},{"name":"Bruch","form_include":false,"optional":true,"type":"uint8"},{"name":"Sonst","form_include":false,"optional":true,"type":"string"},{"name":"Klass","form_include":false,"optional":true,"type":"string"},{"name":"ZSt.","form_include":false,"optional":true,"type":"string"},{"name":"H","add_difference":true,"type":"float64"},{"name":"Typ","override_name":"Typ-H","form_include":false,"optional":true,"type":"string"},{"name":"K","form_include":false,"optional":true,"type":"float64"},{"name":"H-BHK","form_include":false,"optional":true,"type":"float64"},{"name":"Typ","override_name":"Typ-H-BHK","form_include":false,"optional":true,"type":"string"},{"name":"H-Mod","form_include":false,"optional":true,"type":"float64"},{"name":"Typ","override_name":"Typ-H-Mod","optional":true,"form_include":false,"type":"string"}]}"""
default_column_scheme_path = Path('./config/columns.json')
