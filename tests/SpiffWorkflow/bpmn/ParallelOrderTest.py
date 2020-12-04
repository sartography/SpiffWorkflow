# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class MultiInstanceTest(BpmnWorkflowTestCase):
    """The example bpmn diagram has a 4 parallel workflows, this
    verifies that the parallel tasks have a natural order that follows
    the visual layout of the diagram, rather than just the order in which
    they were created. """

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('ParallelOrder.bpmn','ParallelOrder')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)

        self.workflow.do_engine_steps()
        self.assertFalse(self.workflow.is_completed())
        self.assertEquals(4, len(self.workflow.get_ready_user_tasks()))
        tasks = self.workflow.get_ready_user_tasks()
        self.assertEquals("Task 1", tasks[0].get_description())
        self.assertEquals("Task 2", tasks[1].get_description())
        self.assertEquals("Task 3", tasks[2].get_description())
        self.assertEquals("Task 4", tasks[3].get_description())

        nav = self.workflow.get_nav_list()
        self.assertNav(nav[2], description="Task 1")
        self.assertNav(nav[3], description="Task 2")
        self.assertNav(nav[4], description="Task 3")
        self.assertNav(nav[5], description="Task 4")



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MultiInstanceTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
