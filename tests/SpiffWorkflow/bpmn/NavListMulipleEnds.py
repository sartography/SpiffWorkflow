# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class NavListExclusiveGatewayTest(BpmnWorkflowTestCase):
    """The example bpmn diagram looks roughly like this, a gateway
    that leads to two different end points

    [Step 1] -> <x exclusive gateway x>
                        -> 'False'  -> [Alternate End] -> END A
                        -> 'True'  -> [Step 2] -> END B
    """

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('ExclusiveGatewayMultipleEndNavigation.bpmn','ExclusiveGatewayMultipleEndNavigation')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        nav_list = self.workflow.get_nav_list()
        self.assertEqual(6, len(nav_list))

        self.assertEqual("Step 1", nav_list[0]["description"])
        self.assertEqual("GatewayToEnd", nav_list[1]["description"])
        self.assertEqual("False", nav_list[2]["description"])
        self.assertEqual("Step End", nav_list[3]["description"])
        self.assertEqual("True", nav_list[4]["description"])
        self.assertEqual("Step 2", nav_list[5]["description"])

        self.assertEqual(0, nav_list[0]["indent"])


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NavListExclusiveGatewayTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
