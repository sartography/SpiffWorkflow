# -*- coding: utf-8 -*-
from __future__ import division
import unittest
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class InvalidWorkflowsTest(BpmnWorkflowTestCase):

    def testDisconnectedBoundaryEvent(self):
        try:
            self.load_workflow_spec('Invalid-Workflows/Disconnected-Boundary-Event.bpmn20.xml', 'Disconnected Boundary Event')
            self.fail("self.load_workflow_spec('Invalid-Workflows/Disconnected-Boundary-Event.bpmn20.xml', 'Disconnected Boundary Event') should fail.")
        except ValidationException as ex:
            self.assertTrue('This might be a Boundary Event that has been disconnected' in ('%r'%ex),
                '\'This might be a Boundary Event that has been disconnected\' should be a substring of error message: \'%r\'' % ex)
#            self.assertTrue('line 64' in ('%r'%ex),
#                '\'line 64\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Disconnected-Boundary-Event.bpmn20.xml' in ('%r'%ex),
                '\'Disconnected-Boundary-Event.bpmn20.xml\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('intermediateCatchEvent' in ('%r'%ex),
                '\'intermediateCatchEvent\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('sid-84C7CE67-D0B6-486A-B097-486DA924FF9D' in ('%r'%ex),
                '\'sid-84C7CE67-D0B6-486A-B097-486DA924FF9D\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Test Message' in ('%r'%ex),
                '\'Test Message\' should be a substring of error message: \'%r\'' % ex)

    def testNoStartEvent(self):
        try:
            self.load_workflow_spec('Invalid-Workflows/No-Start-Event.bpmn20.xml', 'No Start Event')
            self.fail("self.load_workflow_spec('Invalid-Workflows/No-Start-Event.bpmn20.xml', 'No Start Event') should fail.")
        except ValidationException as ex:
            self.assertTrue('No start event found' in ('%r'%ex),
                '\'No start event found\' should be a substring of error message: \'%r\'' % ex)
#            self.assertTrue('line 10' in ('%r'%ex),
#                '\'line 10\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('No-Start-Event.bpmn20.xml' in ('%r'%ex),
                '\'No-Start-Event.bpmn20.xml\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('process' in ('%r'%ex),
                '\'process\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('sid-669ddebf-4196-41ee-8b04-bcc90bc5f983' in ('%r'%ex),
                '\'sid-669ddebf-4196-41ee-8b04-bcc90bc5f983\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('No Start Event' in ('%r'%ex),
                '\'No Start Event\' should be a substring of error message: \'%r\'' % ex)

    def testMultipleStartEvents(self):
        try:
            self.load_workflow_spec('Invalid-Workflows/Multiple-Start-Events.bpmn20.xml', 'Multiple Start Events')
            self.fail("self.load_workflow_spec('Invalid-Workflows/Multiple-Start-Events.bpmn20.xml', 'Multiple Start Events') should fail.")
        except ValidationException as ex:
            self.assertTrue('Only one Start Event is supported in each process' in ('%r'%ex),
                '\'Only one Start Event is supported in each process\' should be a substring of error message: \'%r\'' % ex)
#            self.assertTrue('line 10' in ('%r'%ex),
#                '\'line 10\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Multiple-Start-Events.bpmn20.xml' in ('%r'%ex),
                '\'Multiple-Start-Events.bpmn20.xml\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('process' in ('%r'%ex),
                '\'process\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('sid-1e457abc-2ee3-4d60-a4df-d2ddf5b18c2b' in ('%r'%ex),
                '\'sid-1e457abc-2ee3-4d60-a4df-d2ddf5b18c2b\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Multiple Start Events' in ('%r'%ex),
                '\'Multiple Start Events\' should be a substring of error message: \'%r\'' % ex)

    def testSubprocessNotFound(self):
        try:
            self.load_workflow_spec('Invalid-Workflows/Subprocess-Not-Found.bpmn20.xml', 'Subprocess Not Found')
            self.fail("self.load_workflow_spec('Invalid-Workflows/Subprocess-Not-Found.bpmn20.xml', 'Subprocess Not Found') should fail.")
        except ValidationException as ex:
            self.assertTrue('No matching process definition found for \'Missing subprocess\'.' in ('%r'%ex),
                '\'No matching process definition found for \'Missing subprocess\'.\' should be a substring of error message: \'%r\'' % ex)
#            self.assertTrue('line 35' in ('%r'%ex),
#                '\'line 35\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Subprocess-Not-Found.bpmn20.xml' in ('%r'%ex),
                '\'Subprocess-Not-Found.bpmn20.xml\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('callActivity' in ('%r'%ex),
                '\'callActivity\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('sid-617B0E1F-42DB-4D40-9B4C-ED631BF6E43A' in ('%r'%ex),
                '\'sid-617B0E1F-42DB-4D40-9B4C-ED631BF6E43A\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Subprocess for Subprocess Not Found' in ('%r'%ex),
                '\'Subprocess for Subprocess Not Found\' should be a substring of error message: \'%r\'' % ex)

    def testRecursiveSubprocesses(self):
        try:
            self.load_workflow_spec('Invalid-Workflows/Recursive-Subprocesses.bpmn20.xml', 'Recursive Subprocesses')
            self.fail("self.load_workflow_spec('Invalid-Workflows/Recursive-Subprocesses.bpmn20.xml', 'Recursive Subprocesses') should fail.")
        except ValidationException as ex:
            self.assertTrue('Recursive call Activities are not supported' in ('%r'%ex),
                '\'Recursive call Activities are not supported\' should be a substring of error message: \'%r\'' % ex)
#            self.assertTrue('line 97' in ('%r'%ex),
#                '\'line 97\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Recursive-Subprocesses.bpmn20.xml' in ('%r'%ex),
                '\'Recursive-Subprocesses.bpmn20.xml\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('callActivity' in ('%r'%ex),
                '\'callActivity\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('sid-10515BFA-0CEC-4B8B-B3BE-E717DEBA6D89' in ('%r'%ex),
                '\'sid-10515BFA-0CEC-4B8B-B3BE-E717DEBA6D89\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Recursive Subprocesses (callback!)' in ('%r'%ex),
                '\'Recursive Subprocesses (callback!)\' should be a substring of error message: \'%r\'' % ex)

    def testUnsupportedTask(self):
        try:
            self.load_workflow_spec('Invalid-Workflows/Unsupported-Task.bpmn20.xml', 'Unsupported Task')
            self.fail("self.load_workflow_spec('Invalid-Workflows/Unsupported-Task.bpmn20.xml', 'Unsupported Task') should fail.")
        except ValidationException as ex:
            self.assertTrue('There is no support implemented for this task type' in ('%r'%ex),
                '\'There is no support implemented for this task type\' should be a substring of error message: \'%r\'' % ex)
#            self.assertTrue('line 63' in ('%r'%ex),
#                '\'line 63\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Unsupported-Task.bpmn20.xml' in ('%r'%ex),
                '\'Unsupported-Task.bpmn20.xml\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('businessRuleTask' in ('%r'%ex),
                '\'businessRuleTask\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('sid-75EEAB28-3B69-4282-B91A-0F3C97931834' in ('%r'%ex),
                '\'sid-75EEAB28-3B69-4282-B91A-0F3C97931834\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Business Rule Task' in ('%r'%ex),
                '\'Business Rule Task\' should be a substring of error message: \'%r\'' % ex)
def suite():
    return unittest.TestLoader().loadTestsFromTestCase(InvalidWorkflowsTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())