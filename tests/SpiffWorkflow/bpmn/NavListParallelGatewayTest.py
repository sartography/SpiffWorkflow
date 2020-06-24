# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class NavListParallelGatewayTest(BpmnWorkflowTestCase):
    """The example bpmn diagram looks roughtly like this

    [Task 1] -> <x skip to task 3? x>
                        -> 'yes'  ->
                                noop
                        -> 'no'  ->
                            <+> ->
                               [Task 2a]
                               [Task 2b]
                               [Task 2c]
                                ->
                <x exclusive gateway x>    -> [Task 3]

    """

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('ParallelTasksNavigation.bpmn','ParallelTasksNavigation')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        nav_list = self.workflow.get_nav_list()
        self.assertEqual(8, len(nav_list))

        self.assertEqual("Enter Task 1", nav_list[0]["description"])
        self.assertEqual("Skip to Task 3?", nav_list[1]["description"])
        self.assertEqual("Yes", nav_list[2]["description"])
        self.assertEqual("No", nav_list[3]["description"])
        self.assertEqual("Enter Task 2a", nav_list[4]["description"])
        self.assertEqual("Enter Task 2b", nav_list[5]["description"])
        self.assertEqual("Enter Task 2c", nav_list[6]["description"])
        self.assertEqual("Enter Task 3", nav_list[7]["description"])

        self.assertEqual(0, nav_list[0]["indent"])
        self.assertEqual(0, nav_list[1]["indent"])
        self.assertEqual(1, nav_list[2]["indent"])
        self.assertEqual(1, nav_list[3]["indent"])
        self.assertEqual(2, nav_list[4]["indent"])
        self.assertEqual(2, nav_list[5]["indent"])
        self.assertEqual(2, nav_list[6]["indent"])
        self.assertEqual(0, nav_list[7]["indent"])
        x = self.workflow.get_ready_user_tasks()
        x[0].data['skip_to_task_3'] = False
        self.workflow.complete_task_from_id(x[0].id)
        self.workflow.do_engine_steps()
        self.save_restore()
        nav_list = self.workflow.get_nav_list()
        self.assertEqual("Enter Task 1", nav_list[0]["description"])
        self.assertEqual("Skip to Task 3?", nav_list[1]["description"])
        self.assertEqual("Yes", nav_list[2]["description"])
        self.assertEqual("No", nav_list[3]["description"])
        self.assertEqual("Enter Task 2a", nav_list[4]["description"])
        self.assertEqual("Enter Task 2b", nav_list[5]["description"])
        self.assertEqual("Enter Task 2c", nav_list[6]["description"])
        self.assertEqual("Enter Task 3", nav_list[7]["description"])


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NavListParallelGatewayTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
