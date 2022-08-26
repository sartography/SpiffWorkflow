import unittest

from SpiffWorkflow.bpmn.PythonScriptEngine import Box

from .PythonDecisionRunner import PythonDecisionRunner


class DictDotNotationDecisionWeirdCharactersTestClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dmn_files =[
            'dict_dot_notation_decision_weird_characters.dmn',
            'dict_dot_notation_decision_weird_characters_v1_3.dmn',
        ]
        cls.runners = [PythonDecisionRunner(d) for d in dmn_files]

    def test_string_decision_string_output1(self):
        for runner in self.runners:
            data = {"odd_foods": {
                "SPAM_LIKE": {"delicious": False}
            }}
            res = runner.decide(Box(data))
            self.assertEqual(res.description, 'This person has a tongue, brain '
                                              'or sense of smell.')

    data = {"foods": {
        "spam": {"delicious": False}
    }}

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(
        DictDotNotationDecisionWeirdCharactersTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
