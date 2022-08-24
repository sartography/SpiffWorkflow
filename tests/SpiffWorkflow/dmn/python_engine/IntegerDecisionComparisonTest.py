import unittest

from .PythonDecisionRunner import PythonDecisionRunner


class IntegerDecisionComparisonTestClass(unittest.TestCase):
    """
    Doc: https://docs.camunda.org/manual/7.7/user-guide/dmn-engine/
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = PythonDecisionRunner('integer_decision_comparison.dmn', debug='DEBUG')

    def test_integer_decision_string_output1(self):
        res = self.runner.decide({"Age":30})
        self.assertEqual(res.description, '30 Row Annotation')

    def test_integer_decision_string_output2(self):
        res = self.runner.decide({"Age":24})
        self.assertEqual(res.description, 'L Row Annotation')

    def test_integer_decision_string_output3(self):
        res = self.runner.decide({"Age":25})
        self.assertEqual(res.description, 'H Row Annotation')

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(IntegerDecisionComparisonTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
