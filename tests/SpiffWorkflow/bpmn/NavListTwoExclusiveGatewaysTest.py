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
    """This is a complex diagram from production/staging that is
    causing some problems.  Want to assure that resetting token
    does not effect task count in this crazy case. Or if it does
    effect it, it doesn't grow exponentially large."""

    def setUp(self):
        self.spec = self.load_workflow_spec(
            'data/rrt.bpmn',
            'rrt')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testRunThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self, save_restore=False):
        total = 12  # Still seems like a ludicrous number of tasks, but ok.

        # Set the workflow in motion, and assure we have the right
        # number of tasks
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        nl = self.workflow.get_nav_list()
        self.assertEquals(total, len(self.workflow.get_tasks()))
        first_task = self.workflow.get_ready_user_tasks()[0]

        # Tell the exclusive gateway to skip the parallel tasks section.
        # We should still have the same number of tasks.
        data = {'isHumanResearch': True, 'isAnimalUse': True, 'isGrantSupport': True}
        for i in range(10):
            task = self.workflow.get_ready_user_tasks()[0]
            task.data = data
            self.workflow.complete_task_from_id(task.id)
            self.workflow.do_engine_steps()
            if(total != len(self.workflow.get_tasks())):
                print(task.task_spec.description + ":: " + str(len(self.workflow.get_tasks())))
            self.assertTrue(total >= len(self.workflow.get_tasks()))

        # Reset the token to the first user task.
        # We should still have the same number of tasks.
        self.workflow.task_tree.dump()
        first_task.reset_token(reset_data=True)
        print('=-----')
        self.workflow.task_tree.dump()
        self.assertTrue(total >= len(self.workflow.get_tasks()))

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ResetTokenParallelTaskCountTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
