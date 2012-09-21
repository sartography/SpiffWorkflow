import unittest
import datetime
import time
from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn.BpmnWorkflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class InvalidWorkflowsTest(BpmnWorkflowTestCase):

    def testDisconnectedBoundaryEvent(self):
        try:
            self.load_workflow_spec('Invalid-Workflows/Disconnected-Boundary-Event.bpmn20.xml', 'Disconnected Boundary Event')
            self.fail("self.load_workflow_spec('Invalid-Workflows/Disconnected-Boundary-Event.bpmn20.xml', 'Disconnected Boundary Event') should fail.")
        except ValueError, ex:
            self.assertTrue('This might be a Boundary Event that has been disconnected' in ('%r'%ex),
                '\'This might be a Boundary Event that has been disconnected\' should be a substring of error message: \'%r\'' % ex)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(InvalidWorkflowsTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())