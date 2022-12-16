import unittest
from pathlib import Path

PROJECT_ROOT = Path(__name__).parent

if __name__ == '__main__':
    testsuite = unittest.TestLoader().discover(start_dir=str(PROJECT_ROOT / 'vfl2csv'), pattern='*_test.py')
    unittest.TextTestRunner().run(test=testsuite)
