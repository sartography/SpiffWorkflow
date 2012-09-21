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


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(InvalidWorkflowsTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())