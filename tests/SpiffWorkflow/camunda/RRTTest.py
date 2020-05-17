# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
from SpiffWorkflow.exceptions import WorkflowException
__author__ = 'kellym'

from tests.SpiffWorkflow.camunda.BaseTestCase import BaseTestCase


class RRTTest(BaseTestCase):
    """This is a diagram that is causing me some headaches, trying to
    figure out why, then this might become something that tests something
    specific.."""

    def setUp(self):
        self.spec = self.load_workflow_spec(
            'data/rrt.bpmn',
            'rrt')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testRunThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self, save_restore=False):

        self.workflow = BpmnWorkflow(self.spec)
        self.assertEquals(330, len(self.workflow.get_tasks()))
        self.workflow.do_engine_steps()
        self.assertEquals(330, len(self.workflow.get_tasks()))
        if save_restore: self.save_restore()
        self.assertEquals(330, len(self.workflow.get_tasks()))
        task = self.workflow.get_ready_user_tasks()[0]
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        task.reset_token(reset_data=True)
        self.workflow.do_engine_steps()
        self.assertEquals(2794, len(self.workflow.get_tasks()))

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(RRTTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
