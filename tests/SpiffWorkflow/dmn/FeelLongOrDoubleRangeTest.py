import unittest

from decimal import Decimal

from tests.SpiffWorkflow.dmn.DecisionRunner import DecisionRunner


class FeelLongOrDoubleDecisionRangeTestClass(unittest.TestCase):
    """
    Doc: https://docs.camunda.org/manual/7.7/user-guide/dmn-engine/
    """

    def test_long_or_double_decision_string_output_inclusive(self):
        runner = DecisionRunner('long_or_double_decision_range_inclusive_feel.dmn', debug='DEBUG')

        res = runner.decide(Decimal('100.05'))
        self.assertEqual(res.description, '100.05-110.05 Inclusive Annotation')

        res = runner.decide(Decimal('99'))
        self.assertEqual(res.description, 'ELSE Row Annotation')

        res = runner.decide(Decimal('110.05'))
        self.assertEqual(res.description, '100.05-110.05 Inclusive Annotation')

        res = runner.decide(Decimal('111'))
        self.assertEqual(res.description, 'ELSE Row Annotation')

    def test_long_or_double_decision_string_output_exclusive(self):
        runner = DecisionRunner('long_or_double_decision_range_exclusive_feel.dmn', debug='DEBUG')

        res = runner.decide(Decimal('100.05'))
        self.assertEqual(res.description, 'ELSE Row Annotation')

        res = runner.decide(Decimal('101'))
        self.assertEqual(res.description, '100.05-110.05 Exclusive Annotation')

        res = runner.decide(Decimal('110.05'))
        self.assertEqual(res.description, 'ELSE Row Annotation')

        res = runner.decide(Decimal('109'))
        self.assertEqual(res.description, '100.05-110.05 Exclusive Annotation')

    def test_long_or_double_decision_string_output_excl_inclusive(self):
        runner = DecisionRunner('long_or_double_decision_range_excl_inclusive_feel.dmn', debug='DEBUG')

        res = runner.decide(Decimal('100.05'))
        self.assertEqual(res.description, 'ELSE Row Annotation')

        res = runner.decide(Decimal('101'))
        self.assertEqual(res.description, '100.05-110.05 ExclInclusive Annotation')

        res = runner.decide(Decimal('110.05'))
        self.assertEqual(res.description, '100.05-110.05 ExclInclusive Annotation')

        res = runner.decide(Decimal('111'))
        self.assertEqual(res.description, 'ELSE Row Annotation')

    def test_long_or_double_decision_string_output_incl_exclusive(self):
        runner = DecisionRunner('long_or_double_decision_range_incl_exclusive_feel.dmn', debug='DEBUG')

        res = runner.decide(Decimal('100.05'))
        self.assertEqual(res.description, '100.05-110.05 InclExclusive Annotation')

        res = runner.decide(Decimal('99'))
        self.assertEqual(res.description, 'ELSE Row Annotation')

        res = runner.decide(Decimal('110.05'))
        self.assertEqual(res.description, 'ELSE Row Annotation')

        res = runner.decide(Decimal('109'))
        self.assertEqual(res.description, '100.05-110.05 InclExclusive Annotation')

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FeelLongOrDoubleDecisionRangeTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
