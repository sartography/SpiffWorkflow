import unittest

from decimal import Decimal

from tests.SpiffWorkflow.dmn.DecisionRunner import DecisionRunner


class FeelLongOrDoubleDecisionTestClass(unittest.TestCase):
    """
    Doc: https://docs.camunda.org/manual/7.7/user-guide/dmn-engine/
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = DecisionRunner('long_or_double_decision_comparison_feel.dmn', debug='DEBUG')

    def test_long_or_double_decision_string_output1(self):
        res = self.runner.decide(Decimal('30.5'))
        self.assertEqual(res.description, '30.5 Row Annotation')

    def test_long_or_double_decision_stringz_output2(self):
        res = self.runner.decide(Decimal('25.3'))
        self.assertEqual(res.description, 'L Row Annotation')

    def test_long_or_double_decision_string_output3(self):
        res = self.runner.decide(Decimal('25.4'))
        self.assertEqual(res.description, 'H Row Annotation')

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FeelLongOrDoubleDecisionTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
