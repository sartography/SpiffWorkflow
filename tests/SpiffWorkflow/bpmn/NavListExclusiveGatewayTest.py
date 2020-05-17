# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class NavListExclusiveGatewayTest(BpmnWorkflowTestCase):
    """The example bpmn diagram looks roughtly like this

    [Task 1] -> <x exclusive gateway x>
                        -> 'a'  -> [Task 2a]
                        -> 'b'  -> [Task 2b]
                <x exclusive gateway x>    -> [Task 3]

    """

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('ExclusiveGatewayNavigation.bpmn','ExclusiveGatewayNavigation')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        nav_list = self.workflow.get_nav_list()
        self.assertEquals(7, len(nav_list))

        self.assertEquals("Enter Task 1", nav_list[0]["description"])
        self.assertEquals("Decide Which Branch?", nav_list[1]["description"])
        self.assertEquals("a", nav_list[2]["description"])
        self.assertEquals("Enter Task 2a", nav_list[3]["description"])
        self.assertEquals("b", nav_list[4]["description"])
        self.assertEquals("Enter Task 2b", nav_list[5]["description"])
        self.assertEquals("Enter Task 3", nav_list[6]["description"])

        self.assertEquals(0, nav_list[0]["indent"])
        self.assertEquals(0, nav_list[1]["indent"])
        self.assertEquals(1, nav_list[2]["indent"])
        self.assertEquals(2, nav_list[3]["indent"])
        self.assertEquals(1, nav_list[4]["indent"])
        self.assertEquals(2, nav_list[5]["indent"])
        self.assertEquals(0, nav_list[6]["indent"])


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NavListExclusiveGatewayTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
