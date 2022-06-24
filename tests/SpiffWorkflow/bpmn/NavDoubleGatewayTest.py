# -*- coding: utf-8 -*-

import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class NavDoubleGateway(BpmnWorkflowTestCase):
    """The example bpmn diagram looks roughly like this, a gateway
    that leads to two different end points

    [Step 1] -> <x exclusive gateway x>
                        -> 'False'  -> [Return Step 1]
                        -> 'True'  -> [Step 2] -> END
    """

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('DoubleGatewayNavigation.bpmn', 'DoubleGatewayNavigation')
        self.workflow = BpmnWorkflow(spec, subprocesses)


    def testRunThroughHappy(self):

        self.workflow.do_engine_steps()
        nav_list = self.workflow.get_flat_nav_list()
        self.assertEqual(14, len(nav_list))

        self.assertEqual("StartEvent", nav_list[0].spec_type)
        self.assertEqual("Task 1", nav_list[1].description)
        self.assertEqual("Decide Which Branch?", nav_list[2].description)
        self.assertEqual("a", nav_list[3].description)
        self.assertEqual("Enter Task 2a", nav_list[4].description)
        self.assertEqual("flow b or c", nav_list[5].description)
        self.assertEqual(None, nav_list[6].description)
        self.assertEqual("flow b", nav_list[7].description)
        self.assertEqual("Enter Task 2b", nav_list[8].description)
        self.assertEqual("flow_c", nav_list[9].description)
        self.assertEqual("Enter Task 2c", nav_list[10].description)
        self.assertEqual("Enter Task 3", nav_list[11].description)

        for nav_item in nav_list:
            if nav_item.spec_type[-4:] == "Task":
                self.assertIsNotNone(nav_item.task_id)

        # Sanity check on deep nav.
        nav_list = self.workflow.get_deep_nav_list()
        self.assertNav(nav_list[0], spec_type="StartEvent", state="COMPLETED")
        self.assertNav(nav_list[1], description="Task 1", state="READY")
        self.assertNav(nav_list[2], description="Decide Which Branch?")
        self.assertNav(nav_list[2].children[0], description="a")
        self.assertNav(nav_list[2].children[0].children[0], description="Enter Task 2a")
        self.assertNav(nav_list[2].children[1], description="flow b or c")
        self.assertNav(nav_list[3], description="Enter Task 3")


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NavDoubleGateway)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
