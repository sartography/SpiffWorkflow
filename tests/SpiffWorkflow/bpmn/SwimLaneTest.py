# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class SwimLaneTest(BpmnWorkflowTestCase):
    """
    Test sample bpmn document to make sure the nav list
    contains the correct swimlane in the 'lane' component
    and make sure that our waiting tasks accept a lane parameter
    and that it picks up the correct tasks.
    """

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('lanes.bpmn','lanes')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        nav_list = self.workflow.get_flat_nav_list()
        self.assertEqual(9, len(nav_list))
        self.assertNav(nav_list[1], description="Request Feature", lane="A")
        self.assertNav(nav_list[2], description="Clarifying Questions?", lane="B")
        self.assertNav(nav_list[5], description="Clarify Request", lane="A")
        self.assertNav(nav_list[7], description="Implement Feature", lane="B")
        atasks = self.workflow.get_ready_user_tasks(lane="A")
        btasks = self.workflow.get_ready_user_tasks(lane="B")
        self.assertEqual(1, len(atasks))
        self.assertEqual(0, len(btasks))
        task = atasks[0]
        self.assertEqual('Activity_A1', task.task_spec.name)
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        atasks = self.workflow.get_ready_user_tasks(lane="A")
        btasks = self.workflow.get_ready_user_tasks(lane="B")
        self.assertEqual(0, len(atasks))
        self.assertEqual(1, len(btasks))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SwimLaneTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
