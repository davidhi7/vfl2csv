import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from vfl2csv.ArgumentParser import parser


class ArgumentParserTest(unittest.TestCase):

    @patch('sys.stderr', new_callable=StringIO)
    def test_parseargs_0args(self, mock_stderr: StringIO):
        with self.assertRaises(SystemExit):
            parser.parse_args([])
        self.assertRegexpMatches(mock_stderr.getvalue(), r'error: the following arguments are required')

    @patch('sys.stderr', new_callable=StringIO)
    def test_parseargs_1arg(self, mock_stderr: StringIO):
        with self.assertRaises(SystemExit):
            parser.parse_args(['first-arg'])
        self.assertRegexpMatches(mock_stderr.getvalue(), r'error: the following arguments are required')

    def test_parseargs_2args(self):
        result = vars(parser.parse_args(['first-arg', 'second-arg']))
        self.assertTrue(isinstance(result['output'], Path))
        self.assertTrue(isinstance(result['input'], list))
        self.assertTrue(isinstance(result['input'][0], Path))
        self.assertEqual(str(result['output']), 'first-arg')
        self.assertEqual(str(result['input'][0]), 'second-arg')

    def test_parseargs_3args(self):
        result = vars(parser.parse_args(['first-arg', 'second-arg', 'third-arg']))
        self.assertEqual(len(result['input']), 2)
        self.assertEqual(str(result['input'][0]), 'second-arg')
        self.assertEqual(str(result['input'][1]), 'third-arg')


if __name__ == '__main__':
    unittest.main()
