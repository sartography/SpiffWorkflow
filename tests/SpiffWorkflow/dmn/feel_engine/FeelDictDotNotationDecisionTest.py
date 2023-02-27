import unittest

from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import Box

from .FeelDecisionRunner import FeelDecisionRunner


class FeelDictDotNotationDecisionTestClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runner = FeelDecisionRunner('dict_dot_notation_decision_feel.dmn')

    def test_string_decision_string_output1(self):
        data = {"foods": {
            "spam": {"delicious": False}
        }}
        res = self.runner.decide(Box(data))
        self.assertEqual(res.description, 'This person has a tongue, brain '
                                          'or sense of smell.')

    data = {"foods": {
        "spam": {"delicious": False}
    }}
    def test_string_decision_string_output2(self):
        data = {"foods": {
            "spam": {"delicious": True}
        }}
        res = self.runner.decide(Box(data))
        self.assertEqual(res.description, 'This person is lacking many '
                                          'critical decision making skills, '
                                          'or is a viking.')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FeelDictDotNotationDecisionTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
