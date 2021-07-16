import unittest

from tests.SpiffWorkflow.dmn.DecisionRunner import DecisionRunner


class FeelStringDecisionTestClass(unittest.TestCase):
    """
    Doc: https://docs.camunda.org/manual/7.7/user-guide/dmn-engine/
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = DecisionRunner('string_decision_feel.dmn', debug='DEBUG')

    def test_string_decision_string_output1(self):
        res = self.runner.decide('m')
        self.assertEqual(res.description, 'm Row Annotation')

    def test_string_decision_string_output2(self):
        res = self.runner.decide('f')
        self.assertEqual(res.description, 'f Row Annotation')

    def test_string_decision_string_output3(self):
        res = self.runner.decide('y')
        self.assertEqual(res.description, 'NOT x Row Annotation')

    def test_string_decision_string_output4(self):
        res = self.runner.decide('x')
        self.assertEqual(res.description, 'ELSE Row Annotation')

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FeelStringDecisionTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
