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

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(InvalidWorkflowsTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())