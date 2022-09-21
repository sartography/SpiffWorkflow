# -*- coding: utf-8 -*-

import unittest

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.camunda.BaseTestCase import BaseTestCase

__author__ = 'kellym'

class ResetTokenParallelTaskCountTest(BaseTestCase):
    """Assure that setting the token does not effect the overall task
    count. Added this when we discovered that this was growing
    exponentially in some cases.."""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('token_trial_parallel_simple.bpmn', 'token_trial_parallel_simple')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testRunThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self, save_restore=False):
        total = 10  # I would expect there to be 9 tasks, but we get 10.

        # Set the workflow in motion, and assure we have the right
        # number of tasks

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
        task.reset_token({}, reset_data=True)
        print('=-----')
        self.workflow.task_tree.dump()
        self.assertEquals(total, len(self.workflow.get_tasks()))
        self.assertEquals(1, len(self.workflow.get_ready_user_tasks()))

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ResetTokenParallelTaskCountTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
