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


class ResetTokenParallelTaskCountTest(BaseTestCase):
    """Assure that setting the token does not effect the overall task
    count. Added this when we discovered that this was growing
    exponentially in some cases.."""

    def setUp(self):
        self.spec = self.load_workflow_spec(
            'data/token_trial_parallel_simple.bpmn',
            'token_trial_parallel_simple')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testRunThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self, save_restore=False):
        total = 10  # I would expect there to be 9 tasks, but we get 10.

        # Set the workflow in motion, and assure we have the right
        # number of tasks
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        self.assertEquals(total, len(self.workflow.get_tasks()))

        # Tell the exclusive gateway to skip the parallel tasks section.
        # We should still have the same number of tasks.
        data = {'skipParallel': True}
        task = self.workflow.get_ready_user_tasks()[0]
        task.data = data
        self.workflow.complete_task_from_id(task.id)
        self.assertEquals(total, len(self.workflow.get_tasks()))

        # Reset the token to the first user task.
        # We should still have the same number of tasks.
        self.workflow.task_tree.dump()
        task.reset_token(reset_data=True)
        print('=-----')
        self.workflow.task_tree.dump()
        self.assertEquals(total, len(self.workflow.get_tasks()))
        self.assertEquals(1, len(self.workflow.get_ready_user_tasks()))
        ready_nav = [item for item in self.workflow.get_nav_list() if item.state == "READY"]
        self.assertEquals(1, len(ready_nav))

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ResetTokenParallelTaskCountTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
