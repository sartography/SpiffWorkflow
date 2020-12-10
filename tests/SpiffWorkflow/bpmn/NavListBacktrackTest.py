# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class NavListBacktrackTest(BpmnWorkflowTestCase):
    """The example bpmn diagram looks roughly like this, a gateway
    that leads to two different end points

    [Step 1] -> <x exclusive gateway x>
                        -> 'False'  -> [Return Step 1]
                        -> 'True'  -> [Step 2] -> END
    """

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('BacktrackNavigation.bpmn','BacktrackNavigation')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        nav_list = self.workflow.get_flat_nav_list()
        self.assertEqual(9, len(nav_list))

        self.assertNav(nav_list[0], name="StartEvent_1", indent=0)
        self.assertNav(nav_list[1], description="Step 1", indent=0)
        self.assertNav(nav_list[2], description="Gateway", indent=0)
        self.assertNav(nav_list[3], description="True", indent=1)
        self.assertNav(nav_list[4], description="Step 2", indent=2)
        self.assertNav(nav_list[5], description="Step 3", indent=2)
        self.assertNav(nav_list[6], spec_type="EndEvent", indent=2)
        self.assertNav(nav_list[8], description="False", indent=1)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NavListBacktrackTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
