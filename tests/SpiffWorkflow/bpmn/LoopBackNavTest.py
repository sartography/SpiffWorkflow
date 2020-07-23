# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class LoopBackNavTest(BpmnWorkflowTestCase):
    """The example bpmn diagram follows a looping structure where a gateway
    may send the token back to a previously executed task.  This test assures
    that navigation works correctly in that circumstance."""

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('LoopBackNav.bpmn', 'LoopBackNav')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_ready_user_tasks()

        self.assertTrue(len(ready_tasks) == 1)
        task = ready_tasks[0]
        #
        nav = self.workflow.get_nav_list()
        self.assertEquals(4, len(nav), "Navigation should include 4 elements, "
                                       "the task, gateway, and true, false "
                                       "paths.")

        self.assertEquals("Loop Again?", nav[0]['description'])
        self.assertEquals("READY", nav[0]['state'])

        task.data = {"loop_again":True}
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        self.assertFalse(self.workflow.is_completed())
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEquals("Loop Again?", task.task_spec.description)
        nav = self.workflow.get_nav_list()
        self.assertEquals("READY", nav[0]['state'])

        task = self.workflow.get_ready_user_tasks()[0]
        task.data = {"loop_again": False}
        self.workflow.complete_task_from_id(task.id)
        nav = self.workflow.get_nav_list()
        self.assertEquals("COMPLETED", nav[0]['state'])

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(LoopBackNavTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
