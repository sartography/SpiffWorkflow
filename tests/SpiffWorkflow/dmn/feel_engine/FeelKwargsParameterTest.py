import unittest

from .FeelDecisionRunner import FeelDecisionRunner


class FeelStringDecisionTestClass(unittest.TestCase):
    """
    Doc: https://docs.camunda.org/manual/7.7/user-guide/dmn-engine/
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = FeelDecisionRunner('kwargs_parameter_feel.dmn')

    def test_string_decision_string_output1(self):
        res = self.runner.decide({"Gender":'m'})
        self.assertEqual(res.description, 'm Row Annotation')

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FeelStringDecisionTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
