import unittest

from .PythonDecisionRunner import PythonDecisionRunner


class StringIntegerDecisionTestClass(unittest.TestCase):
    """
    Doc: https://docs.camunda.org/manual/7.7/user-guide/dmn-engine/
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = PythonDecisionRunner('string_integer_decision.dmn')

    def test_string_integer_decision_string_output1(self):
        res = self.runner.decide({"Gender":'m', "Age":30})
        self.assertEqual(res.description, 'm30 Row Annotation')

    def test_string_integer_decision_string_output2(self):
        res = self.runner.decide({"Gender":'m', "Age":24})
        self.assertEqual(res.description, 'mL Row Annotation')

    def test_string_integer_decision_string_output3(self):
        res = self.runner.decide({"Gender":'m', "Age":25})
        self.assertEqual(res.description, 'mH Row Annotation')

    def test_string_integer_decision_string_output4(self):
        res = self.runner.decide({"Gender":'f', "Age":-1})
        self.assertEqual(res.description, 'fL Row Annotation')

    def test_string_integer_decision_string_output5(self):
        res = self.runner.decide({"Gender":'x', "Age":0})
        self.assertEqual(res.description, 'ELSE Row Annotation')

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(StringIntegerDecisionTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
