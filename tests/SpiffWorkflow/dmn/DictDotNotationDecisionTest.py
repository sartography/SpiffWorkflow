import unittest

from tests.SpiffWorkflow.dmn.DecisionRunner import DecisionRunner
from SpiffWorkflow.bpmn.PythonScriptEngine import Box


class DictDotNotationDecisionTestClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runner = DecisionRunner('dict_dot_notation_decision.dmn', debug='DEBUG')

    def test_string_decision_string_output1(self):
        data = {"foods": {
            "spam": {"delicious": False}
        }}
        data = Box(data)
        res = self.runner.decide(data)
        self.assertEqual(res.description, 'This person has a tongue, brain '
                                          'or sense of smell.')

    data = Box({"foods": {
        "spam": {"delicious": False}
    }})
    def test_string_decision_string_output2(self):
        data = {"foods": {
            "spam": {"delicious": True}
        }}
        res = self.runner.decide(Box(data))
        self.assertEqual(res.description, 'This person is lacking many '
                                          'critical decision making skills, '
                                          'or is a viking.')

    def test_string_decision_with_kwargs(self):
        data = {"foods": {
            "spam": {"delicious": False}
        }}
        res = self.runner.decide({}, **Box(data))
        self.assertEqual(res.description, 'This person has a tongue, brain '
                                          'or sense of smell.')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(DictDotNotationDecisionTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
