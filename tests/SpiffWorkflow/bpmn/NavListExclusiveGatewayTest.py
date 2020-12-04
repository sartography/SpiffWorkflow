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
        return self.load_workflow_spec('ExclusiveGatewayNavigation.bpmn',
                                       'ExclusiveGatewayNavigation')

    def testRunThroughHappy(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        nav_list = self.workflow.get_nav_list()
        self.assertEquals(10, len(nav_list))

        self.assertNav(nav_list[1], description="Enter Task 1", indent=0)
        self.assertNav(nav_list[2], description="Decide Which Branch?",
                       indent=0)
        self.assertNav(nav_list[3], description="a", indent=1)
        self.assertNav(nav_list[4], description="Enter Task 2a", indent=2)
        self.assertNav(nav_list[5], description="b", indent=1)
        self.assertNav(nav_list[6], description="Enter Task 2b", indent=2)
        self.assertNav(nav_list[7], spec_type="ExclusiveGateway", indent=0)
        self.assertNav(nav_list[8], description="Enter Task 3", indent=0)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(
        NavListExclusiveGatewayTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
