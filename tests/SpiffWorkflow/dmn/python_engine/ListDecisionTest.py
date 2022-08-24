import unittest

from .PythonDecisionRunner import PythonDecisionRunner


class ListDecisionTestClass(unittest.TestCase):
    """
    Doc: https://docs.camunda.org/manual/7.7/user-guide/dmn-engine/
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = PythonDecisionRunner('list_decision.dmn', debug='DEBUG')

    def test_string_decision_string_output1(self):
        res = self.runner.decide({'allergies',["PEANUTS", "SPAM"]})
        self.assertEqual(res.description, 'They are allergic to peanuts')

    def test_string_decision_string_output1(self):
        res = self.runner.decide({'allergies':["SPAM", "SPAM"]})
        self.assertEqual(res.description, 'They are not allergic to peanuts')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ListDecisionTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
