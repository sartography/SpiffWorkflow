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
        nav_list = self.workflow.get_flat_nav_list()
        self.assertEqual(12, len(nav_list))

        self.assertNav(nav_list[0], name="StartEvent_1", indent=0)
        self.assertNav(nav_list[1], description="Make Choices", indent=0)
        self.assertNav(nav_list[2], description="Are you a viking?", indent=0)
        self.assertNav(nav_list[3], description="Yes", indent=1)
        self.assertNav(nav_list[4], description="Select a helmet", indent=2)
        self.assertNav(nav_list[5], description="No", indent=1)
        self.assertNav(nav_list[6], description="Do you eat Spam?", indent=0)
        self.assertNav(nav_list[7], description="Yes", indent=1)
        self.assertNav(nav_list[8], description="Eat plate of spam", indent=2)
        self.assertNav(nav_list[9], description="No", indent=1)
        self.assertNav(nav_list[10], description="Examine your life", indent=0)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NavListExclusiveGatewayTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
