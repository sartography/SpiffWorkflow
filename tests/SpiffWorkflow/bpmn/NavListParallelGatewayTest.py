# -*- coding: utf-8 -*-

import os
import sys
import unittest

dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

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
        spec, subprocesses = self.load_workflow_spec('ParallelTasksNavigation.bpmn','ParallelTasksNavigation')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):

        self.workflow.do_engine_steps()
        nav_list = self.workflow.get_flat_nav_list()
        self.assertNav(nav_list[0], name="StartEvent_1", indent=0)
        self.assertNav(nav_list[1], description="Enter Task 1", indent=0)
        self.assertNav(nav_list[2], description="Skip to Task 3?", indent=0)
        self.assertNav(nav_list[3], description="Yes", indent=1)
        self.assertNav(nav_list[4], description="No", indent=1)
        self.assertNav(nav_list[5], spec_type="ParallelGateway", indent=2)
        self.assertNav(nav_list[6], description="Enter Task 2a", indent=3)
        self.assertNav(nav_list[7], description="Enter Task 2b", indent=3)
        self.assertNav(nav_list[8], description="Enter Task 2b_2", indent=3)
        self.assertNav(nav_list[9], description="Enter Task 2c", indent=3)
        self.assertNav(nav_list[10], spec_type="ParallelGateway", indent=2)
        self.assertNav(nav_list[11], description="Enter Task 3", indent=0)
        self.assertNav(nav_list[12], spec_type="EndEvent", indent=0)

        x = self.workflow.get_ready_user_tasks()
        x[0].data['skip_to_task_3'] = False
        self.workflow.complete_task_from_id(x[0].id)
        self.workflow.do_engine_steps()
        self.save_restore()
        nav_list = self.workflow.get_flat_nav_list()
        self.assertNav(nav_list[2], description="Skip to Task 3?", indent=0, state="COMPLETED")
        self.assertNav(nav_list[6], description="Enter Task 2a", indent=0, state="READY")
        self.assertNav(nav_list[7], description="Enter Task 2b", indent=0, state="READY")
        self.assertNav(nav_list[8], description="Enter Task 2b_2", indent=0, state="MAYBE")
        self.assertNav(nav_list[9], description="Enter Task 2c", indent=0, state="READY")

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NavListParallelGatewayTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
