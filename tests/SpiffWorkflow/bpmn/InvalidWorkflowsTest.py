import unittest
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class InvalidWorkflowsTest(BpmnWorkflowTestCase):

    def testDisconnectedBoundaryEvent(self):
        try:
            self.load_workflow_spec('Invalid-Workflows/Disconnected-Boundary-Event.bpmn20.xml', 'Disconnected Boundary Event')
            self.fail("self.load_workflow_spec('Invalid-Workflows/Disconnected-Boundary-Event.bpmn20.xml', 'Disconnected Boundary Event') should fail.")
        except ValidationException, ex:
            self.assertTrue('This might be a Boundary Event that has been disconnected' in ('%r'%ex),
                '\'This might be a Boundary Event that has been disconnected\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('line 64' in ('%r'%ex),
                '\'line 64\' should be a substring of error message: \'%r\'' % ex)
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
        except ValidationException, ex:
            self.assertTrue('No start event found' in ('%r'%ex),
                '\'No start event found\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('line 10' in ('%r'%ex),
                '\'line 10\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('No-Start-Event.bpmn20.xml' in ('%r'%ex),
                '\'No-Start-Event.bpmn20.xml\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('process' in ('%r'%ex),
                '\'process\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('sid-bf1225ef-8efb-4695-ac8e-d140eacea914' in ('%r'%ex),
                '\'sid-bf1225ef-8efb-4695-ac8e-d140eacea914\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('No Start Event' in ('%r'%ex),
                '\'No Start Event\' should be a substring of error message: \'%r\'' % ex)

    def testMultipleStartEvents(self):
        try:
            self.load_workflow_spec('Invalid-Workflows/Multiple-Start-Events.bpmn20.xml', 'Multiple Start Events')
            self.fail("self.load_workflow_spec('Invalid-Workflows/Multiple-Start-Events.bpmn20.xml', 'Multiple Start Events') should fail.")
        except ValidationException, ex:
            self.assertTrue('Only one Start Event is supported in each process' in ('%r'%ex),
                '\'Only one Start Event is supported in each process\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('line 10' in ('%r'%ex),
                '\'line 10\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Multiple-Start-Events.bpmn20.xml' in ('%r'%ex),
                '\'Multiple-Start-Events.bpmn20.xml\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('process' in ('%r'%ex),
                '\'process\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('sid-2ce8a57d-c2ad-4908-9e52-e9e8f61cdecc' in ('%r'%ex),
                '\'sid-2ce8a57d-c2ad-4908-9e52-e9e8f61cdecc\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Multiple Start Events' in ('%r'%ex),
                '\'Multiple Start Events\' should be a substring of error message: \'%r\'' % ex)

    def testSubprocessNotFound(self):
        try:
            self.load_workflow_spec('Invalid-Workflows/Subprocess-Not-Found.bpmn20.xml', 'Subprocess Not Found')
            self.fail("self.load_workflow_spec('Invalid-Workflows/Subprocess-Not-Found.bpmn20.xml', 'Subprocess Not Found') should fail.")
        except ValidationException, ex:
            self.assertTrue('KeyError(\'Missing subprocess\'' in ('%r'%ex),
                '\'KeyError(\'Missing subprocess\'\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('line 35' in ('%r'%ex),
                '\'line 35\' should be a substring of error message: \'%r\'' % ex)
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
        except ValidationException, ex:
            self.assertTrue('Recursive call Activities are not supported' in ('%r'%ex),
                '\'Recursive call Activities are not supported\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('line 97' in ('%r'%ex),
                '\'line 97\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Recursive-Subprocesses.bpmn20.xml' in ('%r'%ex),
                '\'Recursive-Subprocesses.bpmn20.xml\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('callActivity' in ('%r'%ex),
                '\'callActivity\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('sid-10515BFA-0CEC-4B8B-B3BE-E717DEBA6D89' in ('%r'%ex),
                '\'sid-10515BFA-0CEC-4B8B-B3BE-E717DEBA6D89\' should be a substring of error message: \'%r\'' % ex)
            self.assertTrue('Recursive Subprocesses (callback!)' in ('%r'%ex),
                '\'Recursive Subprocesses (callback!)\' should be a substring of error message: \'%r\'' % ex)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(InvalidWorkflowsTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())