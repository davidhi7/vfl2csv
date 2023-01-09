import unittest
from pathlib import Path

PROJECT_ROOT = Path(__name__).parent

if __name__ == '__main__':
    testsuite = unittest.TestLoader().discover(start_dir=PROJECT_ROOT, pattern='*_test.py')
    unittest.TextTestRunner(verbosity=10).run(test=testsuite)
    """
    for module in ('vfl2csv', 'vfl2csv_base', 'vfl2csv_forms'):
        testsuite = unittest.TestLoader().discover(start_dir=str(PROJECT_ROOT / module), pattern='*_test.py')
        unittest.TextTestRunner().run(test=testsuite)
    """
