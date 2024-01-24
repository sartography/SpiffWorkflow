import datetime
import time

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class TimerIntermediateTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesss = self.load_workflow_spec(
            'Test-Workflows/Timer-Intermediate.bpmn20.xml', 
            'sid-909dfba4-15dd-47b3-b7d4-88330891429a')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesss)

    def testRunThroughHappy(self):

        due_time = (datetime.datetime.now() + datetime.timedelta(seconds=0.01)).isoformat()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.workflow.get_tasks(state=TaskState.READY)[0].set_data(due_time=due_time)

        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))

        time.sleep(0.02)

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))
        self.workflow.refresh_waiting_tasks()
        self.assertEqual(0, len(self.workflow.get_tasks(state=TaskState.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(state=TaskState.READY|TaskState.WAITING)))
