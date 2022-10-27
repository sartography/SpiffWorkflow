# -*- coding: utf-8 -*-

import unittest
import datetime
import time
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class ActionManagementTest(BpmnWorkflowTestCase):
    START_TIME_DELTA=0.05
    FINISH_TIME_DELTA=0.10

    def now_plus_seconds(self, seconds):
        return datetime.datetime.now() + datetime.timedelta(seconds=seconds)

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('Test-Workflows/Action-Management.bpmn20.xml', 'Action Management')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)

        start_time = self.now_plus_seconds(self.START_TIME_DELTA)
        finish_time = self.now_plus_seconds(self.FINISH_TIME_DELTA)

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.workflow.get_tasks(TaskState.READY)[0].set_data(
            start_time=start_time, finish_time=finish_time)

    def testRunThroughHappy(self):
        self.do_next_exclusive_step("Review Action", choice='Approve')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual('NEW ACTION', self.workflow.get_tasks(
            TaskState.READY)[0].get_data('script_output'))
        self.assertEqual('Cancel Action (if necessary)',
                          self.workflow.get_tasks(TaskState.READY)[0].task_spec.description)

        time.sleep(self.START_TIME_DELTA)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step("Start Work")
        self.workflow.do_engine_steps()

        self.do_next_named_step("Complete Work", choice="Done")
        self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())

    def testRunThroughOverdue(self):
        self.do_next_exclusive_step("Review Action", choice='Approve')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual('Cancel Action (if necessary)',
                          self.workflow.get_tasks(TaskState.READY)[0].task_spec.description)

        time.sleep(self.START_TIME_DELTA)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step("Start Work")
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.assertEqual('Finish Time', self.workflow.get_tasks(
            TaskState.WAITING)[1].task_spec.description)
        time.sleep(self.FINISH_TIME_DELTA)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.assertNotEqual(
            'Finish Time', self.workflow.get_tasks(TaskState.WAITING)[0].task_spec.description)

        overdue_escalation_task = [
            t for t in self.workflow.get_tasks() if t.task_spec.description == 'Overdue Escalation']
        self.assertEqual(1, len(overdue_escalation_task))
        overdue_escalation_task = overdue_escalation_task[0]
        self.assertEqual(TaskState.COMPLETED, overdue_escalation_task.state)
        self.assertEqual(
            'ACTION OVERDUE', overdue_escalation_task.get_data('script_output'))

        self.do_next_named_step("Complete Work", choice="Done")
        self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())

    def testRunThroughCancel(self):

        self.do_next_exclusive_step("Review Action", choice='Cancel')
        self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())

    def testRunThroughCancelAfterApproved(self):
        self.do_next_exclusive_step("Review Action", choice='Approve')
        self.workflow.do_engine_steps()

        self.do_next_named_step("Cancel Action (if necessary)")
        self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())
        self.assertEqual(
            'ACTION CANCELLED', self.workflow.get_data('script_output'))

    def testRunThroughCancelAfterWorkStarted(self):
        self.do_next_exclusive_step("Review Action", choice='Approve')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        time.sleep(self.START_TIME_DELTA)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step("Start Work")
        self.workflow.do_engine_steps()

        self.do_next_named_step("Cancel Action (if necessary)")
        self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())
        self.assertEqual(
            'ACTION CANCELLED', self.workflow.get_data('script_output'))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ActionManagementTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
