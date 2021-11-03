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
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        task = self.workflow.get_ready_user_tasks()[0]
        task.data = {"cats": 10}
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('NavLeapFrog.bpmn','NavLeapFrog')

    def testRunThroughFlatNav(self):

        # Complete a little bit, so we can see the states in action.

        nav_list = self.workflow.get_flat_nav_list()
        self.assertEqual(21, len(nav_list))

        self.assertNav(nav_list[0], name="StartEvent_1", indent=0, state="COMPLETED")
        self.assertNav(nav_list[1], description="Get Data", indent=0, state="COMPLETED")
        self.assertNav(nav_list[2], description="how many cats", indent=0)
        self.assertNav(nav_list[3], description="many a cat", indent=1)
        self.assertNav(nav_list[4], description="Tell me bout da cats", indent=2, state="READY")
        self.assertNav(nav_list[5], description="no cats", indent=1)
        self.assertNav(nav_list[6], description="Get som dem cats", indent=2)
        self.assertNav(nav_list[7], description="how many cows", indent=0)
        self.assertNav(nav_list[8], description="1 or more cows", indent=1)
        self.assertNav(nav_list[9], description="Tell me bout dem cows", indent=2)
        self.assertNav(nav_list[10], description="no cows", indent=1)
        self.assertNav(nav_list[11], description="How many chickens", indent=0)
        self.assertNav(nav_list[12], description="1 or more chicks", indent=1)
        self.assertNav(nav_list[13], description="Tell me bout da Chikens", indent=2)
        self.assertNav(nav_list[14], description="no chickens", indent=1)
        self.assertNav(nav_list[15], description="How many Pigs?", indent=0)
        self.assertNav(nav_list[16], description="no pigs", indent=1)
        self.assertNav(nav_list[17], description="1 or more pigs", indent=1)
        self.assertNav(nav_list[18], description="Tell me boud dem Pigs", indent=2)
        self.assertNav(nav_list[19], spec_type="EndEvent", indent=0)

    def testRunThroughDeepNav(self):

        nav_list = self.workflow.get_deep_nav_list()
        self.assertEqual(8, len(nav_list))
        self.assertNav(nav_list[0], name="StartEvent_1", indent=0, state="COMPLETED")
        self.assertNav(nav_list[1], description="Get Data", indent=0, state="COMPLETED")
        self.assertNav(nav_list[2], description="how many cats", indent=0, state="READY")
        self.assertNav(nav_list[3], description="how many cows", indent=0, state="MAYBE")
        self.assertNav(nav_list[4], description="How many chickens", indent=0, state="MAYBE")
        self.assertNav(nav_list[5], description="How many Pigs?", indent=0, state=None)
        self.assertNav(nav_list[6], spec_type="EndEvent", indent=0, state=None)

        # Cats
        self.assertNav(nav_list[2].children[0], description="many a cat", state="READY")
        self.assertNav(nav_list[2].children[0].children[0], description="Tell me bout da cats", state="READY")
        self.assertNav(nav_list[2].children[1], description="no cats", indent=1, state=None)
        self.assertNav(nav_list[2].children[1].children[0], description="Get som dem cats")

        # Cows
        self.assertNav(nav_list[3].children[0], description="1 or more cows", state=None)
        self.assertNav(nav_list[3].children[0].children[0], description="Tell me bout dem cows", state=None)
        self.assertNav(nav_list[3].children[1], description="no cows", indent=1, state=None)

        # Chickens
        self.assertNav(nav_list[4].children[0], description="1 or more chicks", state=None)
        self.assertNav(nav_list[4].children[0].children[0], description="Tell me bout da Chikens", state=None)
        self.assertNav(nav_list[4].children[1], description="no chickens", indent=1)

        # Pigs
        self.assertNav(nav_list[5].children[0], description="no pigs", state=None)
        self.assertNav(nav_list[5].children[1], description="1 or more pigs", state=None)
        self.assertNav(nav_list[5].children[1].children[0], description="Tell me boud dem Pigs", state=None)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NavLeapfrogTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
