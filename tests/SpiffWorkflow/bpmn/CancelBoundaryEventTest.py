# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'michaelc'


class CancelBoundaryTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('message_event.bpmn', 'Process_1dagb7t')

    def testBoundaryNavigation(self):
        # get the workflow
        self.workflow = BpmnWorkflow(self.spec)
        # do engine steps
        self.workflow.do_engine_steps()
        nav = self.workflow.get_flat_nav_list()
        nav_deep = self.workflow.get_deep_nav_list()
        self.assertEquals(7, len(nav))
        self.assertNav(nav_item=nav[4], state="MAYBE", description="TokenReset")

        ready_tasks = self.workflow.get_tasks(Task.READY)
        ready_tasks[0].update_data(data={'formdata': 'asdf'})
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()
        nav = self.workflow.get_flat_nav_list()
        print(nav)
        self.assertEquals(7, len(nav))
        self.assertNav(nav_item=nav[4], state="WAITING", description="TokenReset")

    def testCancelEvent(self):
        # get the workflow
        self.workflow = BpmnWorkflow(self.spec)
        # do engine steps
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(Task.READY)
        # task = ready_tasks[0]
        # task is Activity_GetData which has a form
        ready_tasks[0].update_data(data={'formdata': 'asdf'})
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.save_restore()
        # refresh and do engine steps again
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        # this gets us to Activity_HowMany, where we cancel the workflow
        self.workflow.cancel_notify()
        self.assertEqual(self.workflow.last_task.data['title'], 'New Title')
        # assert that Activity_TestMessage state is Completed
        self.assertEqual(self.workflow.last_task.get_name(), 'Activity_TestMessage')
        self.assertEqual(self.workflow.last_task.get_state(), 32)

    def testNoCancelEvent(self):
        # get the workflow
        self.workflow = BpmnWorkflow(self.spec)
        # do engine steps
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(Task.READY)
        # task = ready_tasks[0]
        # task is Activity_GetData which has a form
        ready_tasks[0].update_data(data={'formdata': 'asdf'})
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        # refresh and do engine steps again
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        # this time we don't cancel
        # 'title' should not be in last_task.data
        self.assertNotIn('title', self.workflow.last_task.data)
        # and Activity_HowMany should be Completed
        self.assertEqual(self.workflow.last_task.get_name(), 'Activity_HowMany.BoundaryEventParent')
        self.assertEqual(self.workflow.last_task.get_state(), 32)



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CancelBoundaryTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
