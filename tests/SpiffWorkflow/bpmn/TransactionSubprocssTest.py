# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'michaelc'


class TransactionSubprocessTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('transaction.bpmn', 'Main_Process')

    def testBoundaryNavigation(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        nav = self.workflow.get_flat_nav_list()
        self.assertEqual(17, len(nav))
        self.assertNav(nav_item=nav[2], state="WAITING", description="Cancel Event")

        ready_tasks = self.workflow.get_tasks(Task.READY)
        ready_tasks[0].update_data({'value': 'asdf'})
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()
        nav = self.workflow.get_flat_nav_list()
        self.assertEquals(17, len(nav))
        self.assertNav(nav_item=nav[2], state="WAITING", description="Cancel Event")

    def testCancelEvent(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        tasks = self.workflow.get_tasks()
        ready_tasks = self.workflow.get_tasks(Task.READY)
        # task is Activity_Get_Data which has a form
        ready_tasks[0].update_data({'value': 'asdf'})
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.save_restore()
        # refresh and do engine steps again
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        # this gets us to Activity_Get_Quantity, where we cancel the workflow
        self.workflow.cancel_notify()
        #self.assertIn('cancelled_event', self.workflow.last_task.data)
        # assert that Activity_Cancelled_Event state is Completed
        self.workflow.do_engine_steps()
        self.assertNotIn('value', self.workflow.last_task.data)
        self.assertIn('test_cancel', self.workflow.last_task.data)
        self.assertEqual(self.workflow.last_task.get_name(), 'Cancelled_Event_Action')
        self.assertEqual(self.workflow.last_task.get_state(), 32)

    def testNoCancelEvent(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(Task.READY)
        ready_tasks[0].update_data({'value': 'asdf'})
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(Task.READY)
        ready_tasks[0].update_data({'quantity': 2})
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()
        # this time we don't cancel
        self.assertIn('value', self.workflow.last_task.data)
        self.assertNotIn('test_cancel', self.workflow.last_task.data)
        # and Subprocess should be Completed
        subprocess = self.workflow.get_tasks_from_spec_name('Subprocess')[0]
        self.assertEqual(subprocess.get_state(), 32)

    def testSubworkflowCancelEvent(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(Task.READY)
        ready_tasks[0].update_data({'value': 'asdf'})
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(Task.READY)
        # Subprocess cancelled if quantity < 0
        ready_tasks[0].update_data({'quantity': -1})
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()
        self.assertNotIn('value', self.workflow.last_task.data)
        self.assertIn('test_cancel', self.workflow.last_task.data)
        self.assertEqual(self.workflow.last_task.get_name(), 'Cancelled_Event_Action')
        self.assertEqual(self.workflow.last_task.get_state(), 32)      

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TransactionSubprocessTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
