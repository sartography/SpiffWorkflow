# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class CallActivityTest(BpmnWorkflowTestCase):
    """The example bpmn diagram has a single task with a loop cardinality of 5.
    It should repeat 5 times before termination."""

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('call_activity_*.bpmn','Process_8200379')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        print('-----------')
        print(self.workflow.last_task.task_spec.name)
        #self.assertIn('Workflow',self.workflow.last_task.task_spec.documentation)



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CallActivityTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
