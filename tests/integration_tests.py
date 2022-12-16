import unittest
import subprocess
import sys


class IntegrationTest(unittest.TestCase):
    interpreter = sys.executable
    silent_subprocess_kwargs = {'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}

    def test_arguments_count_validation(self):
        expected_fails = list()
        expected_fails.append(subprocess.run([self.interpreter, 'vfl2csv'], **self.silent_subprocess_kwargs))
        expected_fails.append(subprocess.run([self.interpreter, 'vfl2csv', '1'], **self.silent_subprocess_kwargs))
        for result in expected_fails:
            self.assertEqual(result.returncode, 1)

    def test_argument_path_validation(self):
        result = subprocess.run([self.interpreter, 'vfl2csv', 'invalid-path', 'out'], **self.silent_subprocess_kwargs)
        self.assertEqual(result.returncode, 1)


if __name__ == '__main__':
    unittest.main()
