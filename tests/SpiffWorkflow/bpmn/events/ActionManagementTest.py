import datetime
import time

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class ActionManagementTest(BpmnWorkflowTestCase):
    START_TIME_DELTA=0.05
    FINISH_TIME_DELTA=0.10

    def now_plus_seconds(self, seconds):
        return (datetime.datetime.now() + datetime.timedelta(seconds=seconds)).isoformat()

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec(
            'Test-Workflows/Action-Management.bpmn20.xml',
            'sid-efb89bb6-299a-4dc4-a50a-4286ec490604')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)

        start_time = self.now_plus_seconds(self.START_TIME_DELTA)
        finish_time = self.now_plus_seconds(self.FINISH_TIME_DELTA)

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.workflow.get_tasks(state=TaskState.READY)[0].set_data(start_time=start_time, finish_time=finish_time)

    def testRunThroughHappy(self):
        self.do_next_exclusive_step("Review Action", choice='Approve')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.assertEqual('NEW ACTION', self.workflow.get_tasks(state=TaskState.READY)[0].get_data('script_output'))
        self.assertEqual('Cancel Action (if necessary)', self.workflow.get_tasks(state=TaskState.READY)[0].task_spec.bpmn_name)

        time.sleep(self.START_TIME_DELTA)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(2, len(self.workflow.get_tasks(state=TaskState.READY)))

        self.do_next_named_step("Start Work")
        self.workflow.do_engine_steps()

        self.do_next_named_step("Complete Work", choice="Done")
        self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())

    def testRunThroughOverdue(self):
        self.do_next_exclusive_step("Review Action", choice='Approve')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.assertEqual('Cancel Action (if necessary)', self.workflow.get_tasks(state=TaskState.READY)[0].task_spec.bpmn_name)

        time.sleep(self.START_TIME_DELTA)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(2, len(self.workflow.get_tasks(state=TaskState.READY)))

        self.do_next_named_step("Start Work")
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual('Finish Time', self.workflow.get_next_task(state=TaskState.WAITING).task_spec.bpmn_name)
        time.sleep(self.FINISH_TIME_DELTA)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEqual(2, len(self.workflow.get_tasks(state=TaskState.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertNotEqual('Finish Time', self.workflow.get_tasks(state=TaskState.WAITING)[0].task_spec.bpmn_name)

        overdue_escalation_task = [
            t for t in self.workflow.get_tasks() if t.task_spec.bpmn_name == 'Overdue Escalation']
        self.assertEqual(1, len(overdue_escalation_task))
        overdue_escalation_task = overdue_escalation_task[0]
        self.assertEqual(TaskState.COMPLETED, overdue_escalation_task.state)
        self.assertEqual('ACTION OVERDUE', overdue_escalation_task.get_data('script_output'))

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
        self.assertEqual('ACTION CANCELLED', self.workflow.get_data('script_output'))

    def testRunThroughCancelAfterWorkStarted(self):
        self.do_next_exclusive_step("Review Action", choice='Approve')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))

        time.sleep(self.START_TIME_DELTA)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(2, len(self.workflow.get_tasks(state=TaskState.READY)))

        self.do_next_named_step("Start Work")
        self.workflow.do_engine_steps()

        self.do_next_named_step("Cancel Action (if necessary)")
        self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())
        self.assertEqual('ACTION CANCELLED', self.workflow.get_data('script_output'))
