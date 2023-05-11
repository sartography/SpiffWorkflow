from SpiffWorkflow.bpmn.parser.util import full_tag
from SpiffWorkflow.camunda.specs.user_task import UserTask
from SpiffWorkflow.camunda.specs.business_rule_task import BusinessRuleTask
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.parser.task_spec import UserTaskParser, BusinessRuleTaskParser


from .BaseTestCase import BaseTestCase

class CamundaParserTest(BaseTestCase):

    def setUp(self):
        self.parser = CamundaParser()

    def test_overrides(self):

        overrides = [
            ('userTask', UserTaskParser, UserTask),
            ('businessRuleTask', BusinessRuleTaskParser, BusinessRuleTask),
        ]

        for key, parser, spec in overrides:
            self.assertIn(full_tag(key), self.parser.OVERRIDE_PARSER_CLASSES)
            self.assertEqual((parser, spec), self.parser.OVERRIDE_PARSER_CLASSES.get(full_tag(key)))