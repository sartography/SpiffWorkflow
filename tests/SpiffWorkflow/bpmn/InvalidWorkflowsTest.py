# -*- coding: utf-8 -*-
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class InvalidWorkflowsTest(BpmnWorkflowTestCase):

    def testNoStartEvent(self):
        try:
            self.load_workflow_spec(
                'Invalid-Workflows/No-Start-Event.bpmn20.xml', 'sid-669ddebf-4196-41ee-8b04-bcc90bc5f983')
            self.fail("self.load_workflow_spec('Invalid-Workflows/No-Start-Event.bpmn20.xml', 'No Start Event') should fail.")
        except ValidationException as ex:
            self.assertTrue('No start event found' in ('%r' % ex),
                            '\'No start event found\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('No-Start-Event.bpmn20.xml' in ex.file_name,
                            '\'No-Start-Event.bpmn20.xml\' should be a substring of error message: \'%r\'' % ex)

    def testCallActivityNotFound(self):

        with self.assertRaises(ValidationException) as exc:
            self.load_workflow_spec('Invalid-Workflows/Subprocess-Not-Found.bpmn20.xml', 'Subprocess Not Found')
            self.assertIn("The process 'Missing subprocess' was not found.", str(exc))
            self.assertIn("bpmn:callActivity (id:sid-617B0E1F-42DB-4D40-9B4C-ED631BF6E43A)", str(exc))
            self.assertIn("Invalid-Workflows/Subprocess-Not-Found.bpmn20.xml", str(exc))

    def testUnsupportedTask(self):
        try:
            self.load_workflow_spec('Invalid-Workflows/Unsupported-Task.bpmn20.xml', 'sid-00c10a31-5eb4-4f6c-a3eb-3664035ca9a7')
            self.fail("self.load_workflow_spec('Invalid-Workflows/Unsupported-Task.bpmn20.xml', 'Unsupported Task') should fail.")
        except ValidationException as ex:
            self.assertTrue(
                'There is no support implemented for this task type' in ( '%r' % ex),
                '\'There is no support implemented for this task type\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Unsupported-Task.bpmn20.xml' in ex.file_name,
                            '\'Unsupported-Task.bpmn20.xml\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('businessRuleTask' in ex.tag,
                            '\'businessRuleTask\' should be a substring of the tag: \'%r\'' % ex)
            self.assertTrue('Business Rule Task' in ex.name,
                            '\'Business Rule Task\' should be the name: \'%s\'' % ex.name)

