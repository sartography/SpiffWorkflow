import unittest

from .PythonDecisionRunner import PythonDecisionRunner


class IntegerDecisionRangeTestClass(unittest.TestCase):
    """
    Doc: https://docs.camunda.org/manual/7.7/user-guide/dmn-engine/
    """

    def test_integer_decision_string_output_inclusive(self):
        runner = PythonDecisionRunner('integer_decision_range_inclusive.dmn')

        res = runner.decide({"Age":100})
        self.assertEqual(res.description, '100-110 Inclusive Annotation')

        res = runner.decide({"Age":99})
        self.assertEqual(res.description, 'ELSE Row Annotation')

        res = runner.decide({"Age":110})
        self.assertEqual(res.description, '100-110 Inclusive Annotation')

        res = runner.decide({"Age":111})
        self.assertEqual(res.description, 'ELSE Row Annotation')

    def test_integer_decision_string_output_exclusive(self):
        runner = PythonDecisionRunner('integer_decision_range_exclusive.dmn')

        res = runner.decide({"Age":100})
        self.assertEqual(res.description, 'ELSE Row Annotation')

        res = runner.decide({"Age":101})
        self.assertEqual(res.description, '100-110 Exclusive Annotation')

        res = runner.decide({"Age":110})
        self.assertEqual(res.description, 'ELSE Row Annotation')

        res = runner.decide({"Age":109})
        self.assertEqual(res.description, '100-110 Exclusive Annotation')

    def test_integer_decision_string_output_excl_inclusive(self):
        runner = PythonDecisionRunner('integer_decision_range_excl_inclusive.dmn')

        res = runner.decide({"Age":100})
        self.assertEqual(res.description, 'ELSE Row Annotation')

        res = runner.decide({"Age":101})
        self.assertEqual(res.description, '100-110 ExclInclusive Annotation')

        res = runner.decide({"Age":110})
        self.assertEqual(res.description, '100-110 ExclInclusive Annotation')

        res = runner.decide({"Age":111})
        self.assertEqual(res.description, 'ELSE Row Annotation')

    def test_integer_decision_string_output_incl_exclusive(self):
        runner = PythonDecisionRunner('integer_decision_range_incl_exclusive.dmn')

        res = runner.decide({"Age":100})
        self.assertEqual(res.description, '100-110 InclExclusive Annotation')

        res = runner.decide({"Age":99})
        self.assertEqual(res.description, 'ELSE Row Annotation')

        res = runner.decide({"Age":110})
        self.assertEqual(res.description, 'ELSE Row Annotation')

        res = runner.decide({"Age":109})
        self.assertEqual(res.description, '100-110 InclExclusive Annotation')

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(IntegerDecisionRangeTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
