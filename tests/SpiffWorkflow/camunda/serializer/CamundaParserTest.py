import unittest

from SpiffWorkflow.camunda.parser.UserTaskParser import UserTaskParser
from SpiffWorkflow.camunda.specs.UserTask import UserTask
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser


class CamundaParserTest(unittest.TestCase):
    CORRELATE = CamundaParser

    def setUp(self):
        self.parser = CamundaParser()

    def test_overrides(self):
        expected_key = "{http://www.omg.org/spec/BPMN/20100524/MODEL}userTask"
        self.assertIn(expected_key,
                      self.parser.OVERRIDE_PARSER_CLASSES)

        self.assertEqual((UserTaskParser, UserTask),
                         self.parser.OVERRIDE_PARSER_CLASSES.get(expected_key))
