import unittest

from SpiffWorkflow.dmn.parser.BusinessRuleTaskParser import BusinessRuleTaskParser
from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.dmn.specs.BuisnessRuleTask import BusinessRuleTask


class BpmnDmnParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = BpmnDmnParser()

    def test_overrides(self):
        expected_key = "{http://www.omg.org/spec/BPMN/20100524/MODEL}businessRuleTask"
        self.assertIn(expected_key,
                      self.parser.OVERRIDE_PARSER_CLASSES)

        self.assertEqual((BusinessRuleTaskParser, BusinessRuleTask),
                         self.parser.OVERRIDE_PARSER_CLASSES.get(expected_key))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BpmnDmnParserTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
