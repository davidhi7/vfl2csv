import unittest
from pathlib import Path

PROJECT_ROOT = Path(__name__).parent

if __name__ == '__main__':
    # make test directory

    testsuite = unittest.TestLoader().discover(start_dir=str(PROJECT_ROOT), pattern='*_test.py')
    result = unittest.TextTestRunner(verbosity=10).run(test=testsuite)
    exit(0 if result.wasSuccessful() else 1)
