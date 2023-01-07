import unittest
from pathlib import Path

PROJECT_ROOT = Path(__name__).parent

if __name__ == '__main__':
    for module in ('vfl2csv', 'vfl2csv_base', 'vfl2csv_forms'):
        testsuite = unittest.TestLoader().discover(start_dir=str(PROJECT_ROOT / module), pattern='*_test.py')
        unittest.TextTestRunner().run(test=testsuite)
