# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class NavLeapfrogTest(BpmnWorkflowTestCase):
    """The example bpmn diagram looks roughly like this, a gateway
    that leads to two different end points

    [Step 1] -> <x exclusive gateway x>
                        -> 'False'  -> [Return Step 1]
                        -> 'True'  -> [Step 2] -> END
    """

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('NavLeapFrog.bpmn','NavLeapFrog')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        nav_list = self.workflow.get_nav_list()
        self.assertEqual(19, len(nav_list))

        self.assertNav(nav_list[0], name="StartEvent_1", indent=0)
        self.assertNav(nav_list[1], description="Get Data", indent=0)
        self.assertNav(nav_list[2], description="how many cats", indent=0)
        self.assertNav(nav_list[3], description="many a cat", indent=1)
        self.assertNav(nav_list[4], description="Tell me bout da cats", indent=2)
        self.assertNav(nav_list[5], description="no cats", indent=1)
        self.assertNav(nav_list[6], description="how many cows", indent=0)
        self.assertNav(nav_list[7], description="1 or more cows", indent=1)
        self.assertNav(nav_list[8], description="Tell me bout dem cows", indent=2)
        self.assertNav(nav_list[9], description="no cows", indent=1)
        self.assertNav(nav_list[10], description="How many chickens", indent=0)
        self.assertNav(nav_list[11], description="1 or more chicks", indent=1)
        self.assertNav(nav_list[12], description="Tell me bout da Chikens", indent=2)
        self.assertNav(nav_list[13], description="no chickens", indent=1)
        self.assertNav(nav_list[14], description="How many Pigs?", indent=0)
        self.assertNav(nav_list[15], description="no pigs", indent=1)
        self.assertNav(nav_list[16], description="1 or more pigs", indent=1)
        self.assertNav(nav_list[17], description="Tell me boud dem Pigs", indent=2)
        self.assertNav(nav_list[18], spec_type="TestEndEvent", indent=0)



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NavLeapfrogTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
