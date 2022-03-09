import unittest

from tests.SpiffWorkflow.dmn.DecisionRunner import DecisionRunner
from SpiffWorkflow.bpmn.PythonScriptEngine import Box


class DictDotNotationDecisionTestClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dmn_files =[
            'dict_dot_notation_decision.dmn',
            'dict_dot_notation_decision_v1_3.dmn',
        ]
        cls.runners = [DecisionRunner(d, debug='DEBUG') for d in dmn_files]

    def test_string_decision_string_output1(self):
        for runner in self.runners:
            data = {"foods": {
                "spam": {"delicious": False}
            }}
            data = Box(data)
            res = runner.decide(data)
            self.assertEqual(res.description, 'This person has a tongue, brain '
                                              'or sense of smell.')

    data = Box({"foods": {
        "spam": {"delicious": False}
    }})

    def test_string_decision_string_output2(self):
        for runner in self.runners:
            data = {"foods": {
                "spam": {"delicious": True}
            }}
            res = runner.decide(Box(data))
            self.assertEqual(res.description, 'This person is lacking many '
                                              'critical decision making skills, '
                                              'or is a viking.')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(DictDotNotationDecisionTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
