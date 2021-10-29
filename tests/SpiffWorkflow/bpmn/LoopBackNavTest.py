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
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('LoopBackNav.bpmn', 'LoopBackNav')

    def testRunThroughHappy(self):

        ready_tasks = self.workflow.get_ready_user_tasks()

        self.assertTrue(len(ready_tasks) == 1)
        task = ready_tasks[0]
        #
        nav = self.workflow.get_flat_nav_list()
        self.assertEqual(9, len(nav), "Navigation should include 6 elements, "
                                       "start, the task, gateway, and true,"
                                       " false, and end paths.")

        self.assertEqual("Loop Again?", nav[1].description)
        self.assertEqual("READY", nav[1].state)

        task.data = {"loop_again":True}
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        self.assertFalse(self.workflow.is_completed())
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual("Why?", task.task_spec.description)
        self.workflow.complete_task_from_id(task.id)
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual("Loop Again?", task.task_spec.description)

        nav = self.workflow.get_flat_nav_list()
        self.assertEqual("Loop Again?", nav[1].description)
        self.assertEqual("READY", nav[1].state)

        task = self.workflow.get_ready_user_tasks()[0]
        task.data = {"loop_again": False}
        self.workflow.complete_task_from_id(task.id)
        nav = self.workflow.get_flat_nav_list()
        self.assertEqual("COMPLETED", nav[1].state)

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

    def testDeepNavigation(self):
        nav = self.workflow.get_deep_nav_list()
        print(nav)
        self.assertNav(nav[1], description="Loop Again?", state="READY")
        self.assertNav(nav[2], spec_type="ExclusiveGateway", state="MAYBE")
        self.assertNav(nav[2].children[1].children[1], description="Loop Again?",
                       backtrack_to=nav[1].name)
        pass

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(LoopBackNavTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
