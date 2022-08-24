import unittest

from .FeelDecisionRunner import FeelDecisionRunner


class FeelStringDecisionTestClass(unittest.TestCase):
    """
    Doc: https://docs.camunda.org/manual/7.7/user-guide/dmn-engine/
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = FeelDecisionRunner('string_decision_feel.dmn', debug='DEBUG')

    def test_string_decision_string_output1(self):
        res = self.runner.decide({"Gender":'m'})
        self.assertEqual(res.description, 'm Row Annotation')

    def test_string_decision_string_output2(self):
        res = self.runner.decide({"Gender":'f'})
        self.assertEqual(res.description, 'f Row Annotation')

    def test_string_decision_string_output3(self):
        res = self.runner.decide({"Gender":'y'})
        self.assertEqual(res.description, 'NOT x Row Annotation')

    def test_string_decision_string_output4(self):
        res = self.runner.decide({"Gender":'x'})
        self.assertEqual(res.description, 'ELSE Row Annotation')

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FeelStringDecisionTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
