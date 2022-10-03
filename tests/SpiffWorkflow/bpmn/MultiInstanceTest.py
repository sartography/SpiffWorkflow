# -*- coding: utf-8 -*-

import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class MultiInstanceTest(BpmnWorkflowTestCase):
    """The example bpmn diagram has a single task with a loop cardinality of 5.
    It should repeat 5 times before termination."""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('bpmnMultiUserTask.bpmn','MultiInstance')
        self.workflow = BpmnWorkflow(spec, subprocesses)


    def testRunThroughHappy(self):

        for i in range(5):
            self.workflow.do_engine_steps()
            self.assertFalse(self.workflow.is_completed())
            self.do_next_exclusive_step('Activity_Loop')

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

    def testSaveRestore(self):

        for i in range(5):
            self.save_restore()
            self.workflow.do_engine_steps()
            self.assertFalse(self.workflow.is_completed())
            self.do_next_exclusive_step('Activity_Loop')

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MultiInstanceTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
