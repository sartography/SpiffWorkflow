# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class NavListExclusiveGatewayTest(BpmnWorkflowTestCase):
    """The example bpmn diagram looks roughtly like this

    [Task 1] -> <x exclusive gateway x> Are you a viking?
                        -> 'yes'  -> [Choose Helmet]
                        -> 'no'  ->
                    <x exclusive gateway x> Do you eat spam?
                            -> 'yes'  -> [Eat plate of spam]
                            -> 'no'  ->
                    <x exclusive gateway x>
                       -> [Examine your life]

    """

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('ExclusiveGatewayTwiceNavigation.bpmn','ExclusiveGatewayTwiceNavigation')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        nav_list = self.workflow.get_nav_list()
        self.assertEquals(10, len(nav_list))

        self.assertEquals("Make Choices", nav_list[0]["description"])
        self.assertEquals("Are you a viking?", nav_list[1]["description"])
        self.assertEquals("Yes", nav_list[2]["description"])
        self.assertEquals("Select a helmet", nav_list[3]["description"])
        self.assertEquals("No", nav_list[4]["description"])
        self.assertEquals("Do you eat Spam?", nav_list[5]["description"])
        self.assertEquals("Yes", nav_list[6]["description"])
        self.assertEquals("Eat plate of spam", nav_list[7]["description"])
        self.assertEquals("No", nav_list[8]["description"])
        self.assertEquals("Examine your life", nav_list[9]["description"])

        self.assertEquals(0, nav_list[0]["indent"])
        self.assertEquals(0, nav_list[1]["indent"])
        self.assertEquals(1, nav_list[2]["indent"])
        self.assertEquals(2, nav_list[3]["indent"])
        self.assertEquals(1, nav_list[4]["indent"])
        self.assertEquals(0, nav_list[5]["indent"])
        self.assertEquals(1, nav_list[6]["indent"])
        self.assertEquals(2, nav_list[7]["indent"])
        self.assertEquals(1, nav_list[8]["indent"])
        self.assertEquals(0, nav_list[9]["indent"])


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NavListExclusiveGatewayTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
