import unittest
from datetime import datetime

from SpiffWorkflow.dmn.parser.DMNParser import DMNParser

from .FeelDecisionRunner import FeelDecisionRunner


class FeelDateDecisionTestClass(unittest.TestCase):
    """
    Doc: https://docs.camunda.org/manual/7.7/user-guide/dmn-engine/
    """

    @classmethod
    def setUpClass(cls):
        cls.runner = FeelDecisionRunner('date_decision_feel.dmn', debug='DEBUG')

    def test_date_decision_string_output1(self):
        res = self.runner.decide(datetime.strptime('2017-11-01T10:00:00', DMNParser.DT_FORMAT))
        self.assertEqual(res.description, '111 Row Annotation')

    def test_date_decision_string_output2(self):
        res = self.runner.decide(datetime.strptime('2017-11-03T00:00:00', DMNParser.DT_FORMAT))
        self.assertEqual(res.description, '311 Row Annotation')

    def test_date_decision_string_output3(self):
        res = self.runner.decide(datetime.strptime('2017-11-02T00:00:00', DMNParser.DT_FORMAT))
        self.assertEqual(res.description, '<3.11 Row Annotation')

    def test_date_decision_string_output4(self):
        res = self.runner.decide(datetime.strptime('2017-11-04T00:00:00', DMNParser.DT_FORMAT))
        self.assertEqual(res.description, '>3.11 Row Annotation')

    def test_date_decision_string_output5(self):
        res = self.runner.decide(datetime.strptime('2017-11-13T12:00:00', DMNParser.DT_FORMAT))
        self.assertEqual(res.description, '>13.11<14.11 Row Annotation')

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FeelDateDecisionTestClass)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
