# -*- coding: utf-8 -*-

from fileinput import filename
import unittest

import os

from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from SpiffWorkflow.signavio.parser.bpmn import SignavioBpmnParser
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class InvalidWorkflowsTest(BpmnWorkflowTestCase):

    def testDisconnectedBoundaryEvent(self):

        with self.assertRaises(ValidationException) as exc:
            parser = SignavioBpmnParser()
            filename = os.path.join(os.path.dirname(__file__), 'data', 'Invalid-Workflows/Disconnected-Boundary-Event.bpmn20.xml')
            parser.add_bpmn_file(filename)
            self.assertIn('Intermediate Catch Event has no incoming sequences', str(exc))
            self.assertIn('bpmn:intermediateCatchEvent (id:sid-84C7CE67-D0B6-486A-B097-486DA924FF9D)', str(exc))
            self.assertIn('Invalid-Workflows/Disconnected-Boundary-Event.bpmn20.xml', str(exc))

    def testNoStartEvent(self):
        try:
            self.load_workflow_spec(
                'Invalid-Workflows/No-Start-Event.bpmn20.xml', 'No Start Event')
            self.fail(
                "self.load_workflow_spec('Invalid-Workflows/No-Start-Event.bpmn20.xml', 'No Start Event') should fail.")
        except ValidationException as ex:
            self.assertTrue('No start event found' in ('%r' % ex),
                            '\'No start event found\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('No-Start-Event.bpmn20.xml' in ('%r' % ex),
                            '\'No-Start-Event.bpmn20.xml\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('process' in ('%r' % ex),
                            '\'process\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue(
                'sid-669ddebf-4196-41ee-8b04-bcc90bc5f983' in ('%r' % ex),
                '\'sid-669ddebf-4196-41ee-8b04-bcc90bc5f983\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('No Start Event' in ('%r' % ex),
                            '\'No Start Event\' should be a substring of error message: \'%r\'' % ex)

    def testSubprocessNotFound(self):
        
        with self.assertRaises(ValidationException) as exc:
            self.load_workflow_spec('Invalid-Workflows/Subprocess-Not-Found.bpmn20.xml', 'Subprocess Not Found')
            self.assertIn("The process 'Missing subprocess' was not found.", str(exc))
            self.assertIn("bpmn:callActivity (id:sid-617B0E1F-42DB-4D40-9B4C-ED631BF6E43A)", str(exc))
            self.assertIn("Invalid-Workflows/Subprocess-Not-Found.bpmn20.xml", str(exc))

    def testUnsupportedTask(self):
        try:
            self.load_workflow_spec(
                'Invalid-Workflows/Unsupported-Task.bpmn20.xml', 'Unsupported Task')
            self.fail(
                "self.load_workflow_spec('Invalid-Workflows/Unsupported-Task.bpmn20.xml', 'Unsupported Task') should fail.")
        except ValidationException as ex:
            self.assertTrue(
                'There is no support implemented for this task type' in (
                    '%r' % ex),
                '\'There is no support implemented for this task type\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Unsupported-Task.bpmn20.xml' in ('%r' % ex),
                            '\'Unsupported-Task.bpmn20.xml\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('businessRuleTask' in ('%r' % ex),
                            '\'businessRuleTask\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue(
                'sid-75EEAB28-3B69-4282-B91A-0F3C97931834' in ('%r' % ex),
                '\'sid-75EEAB28-3B69-4282-B91A-0F3C97931834\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Business Rule Task' in ('%r' % ex),
                            '\'Business Rule Task\' should be a substring of error message: \'%r\'' % ex)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(InvalidWorkflowsTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
