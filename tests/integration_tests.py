import unittest
import subprocess
import sys


class IntegrationTest(unittest.TestCase):
    interpreter = sys.executable
    silent_subprocess_kwargs = {'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}
    

if __name__ == '__main__':
    unittest.main()
