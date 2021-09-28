import unittest

from SpiffWorkflow.bpmn.FeelLikeScriptEngine import FeelLikeScriptEngine
from tests.SpiffWorkflow.dmn.DecisionRunner import DecisionRunner


class FeelListDecisionTestClass(unittest.TestCase):
    """
    Doc: https://docs.camunda.org/manual/7.7/user-guide/dmn-engine/
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = DecisionRunner('list_decision_feel.dmn',
                                    script_engine=FeelLikeScriptEngine(),
                                    debug='DEBUG')

    def test_string_decision_string_output1(self):
        res = self.runner.decide(["PEANUTS", "SPAM"])
        self.assertEqual(res.description, 'They are allergic to peanuts')

    def test_string_decision_string_output1(self):
        res = self.runner.decide(["SPAM", "SPAM"])
        self.assertEqual(res.description, 'They are not allergic to peanuts')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FeelListDecisionTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
