import unittest

from .PythonDecisionRunner import PythonDecisionRunner


class BoolDecisionTestClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runner = PythonDecisionRunner('bool_decision.dmn', debug='DEBUG')

    def test_bool_decision_string_output1(self):
        res = self.runner.decide({'input': True})
        self.assertEqual(res.description, 'Y Row Annotation')

    def test_bool_decision_string_output2(self):
        res = self.runner.decide({'input': False})
        self.assertEqual(res.description, 'N Row Annotation')

    def test_bool_decision_string_output3(self):
        res = self.runner.decide(None)
        self.assertEqual(res.description, 'ELSE Row Annotation')

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BoolDecisionTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
