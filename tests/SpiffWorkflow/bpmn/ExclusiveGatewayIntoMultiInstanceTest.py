# -*- coding: utf-8 -*-



import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class ExclusiveGatewayIntoMultiInstanceTest(BpmnWorkflowTestCase):
    """In the example BPMN Diagram we set x = 0, then we have an
    exclusive gateway that should skip over a parallel multi-instance
    class, so it should run straight through and complete without issue."""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('exclusive_into_multi.bpmn','ExclusiveToMulti')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):

        
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

    def testSaveRestore(self):

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ExclusiveGatewayIntoMultiInstanceTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
