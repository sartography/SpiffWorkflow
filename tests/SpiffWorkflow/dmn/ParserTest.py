import os
import unittest

from .python_engine.PythonDecisionRunner import PythonDecisionRunner

class ParserTest(unittest.TestCase):

    def test_input_dash(self):
        filename = os.path.join(os.path.dirname(__file__) , 'data', 'input_dash.dmn')
        runner = PythonDecisionRunner(filename)
        result = runner.result({'a': ''})
        self.assertDictEqual(result, {'b': 'anything goes'})