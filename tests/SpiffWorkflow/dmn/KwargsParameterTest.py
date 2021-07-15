import unittest

from tests.SpiffWorkflow.dmn.DecisionRunner import DecisionRunner


class StringDecisionTestClass(unittest.TestCase):
    """
    Doc: https://docs.camunda.org/manual/7.7/user-guide/dmn-engine/
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = DecisionRunner('kwargs_parameter.dmn', debug='DEBUG')

    def test_string_decision_string_output1(self):
        res = self.runner.decide(Gender='m')
        self.assertEqual(res.description, 'm Row Annotation')

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(StringDecisionTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
