# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
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
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('DoubleGatewayNavigation.bpmn','DoubleGatewayNavigation')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        nav_list = self.workflow.get_nav_list()
        self.assertEqual(11, len(nav_list))

        self.assertEqual("Task 1", nav_list[0]["description"])
        self.assertEqual("Decide Which Branch?", nav_list[1]["description"])
        self.assertEqual("a", nav_list[2]["description"])
        self.assertEqual("Enter Task 2a", nav_list[3]["description"])
        self.assertEqual("flow b or c", nav_list[4]["description"])
        self.assertEqual(None, nav_list[5]["description"])
        self.assertEqual("flow b", nav_list[6]["description"])
        self.assertEqual("Enter Task 2b", nav_list[7]["description"])
        self.assertEqual(None, nav_list[8]["description"])
        self.assertEqual("Enter Task 2c", nav_list[9]["description"])
        self.assertEqual("Enter Task 3", nav_list[10]["description"])

        self.assertEqual(0, nav_list[0]["indent"])


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NavDoubleGateway)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
