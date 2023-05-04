# -*- coding: utf-8 -*-

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.task import TaskState
from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class ResetTokenOnBoundaryEventTest(BpmnWorkflowTestCase):
    """Assure that when we reset a token to a previous task, and that
    task has a boundary event, that the boundary event is reset to the
    correct state."""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('reset_with_boundary_event.bpmn',
                                                     'token')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testNormal(self):
        self.actualTest(save_restore=False)
    def testSaveRestore(self):
        self.actualTest(save_restore=True)

    def actualTest(self, save_restore=False):
        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_ready_user_tasks()))
        task1 = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual(task1.get_name(), 'First')
        timer_event = self.workflow.get_tasks_from_spec_name('Event_My_Timer')[0]
        self.assertEqual(TaskState.WAITING, timer_event.state)

        task1.run()
        self.workflow.do_engine_steps()
        task2 = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual(task2.get_name(), 'Last')
        timer_event = self.workflow.get_tasks_from_spec_name('Event_My_Timer')[0]
        self.assertEqual(TaskState.CANCELLED, timer_event.state)

        # Here we reset back to the first task
        self.workflow.reset_task_from_id(task1.id)

        # At which point, the timer event should return to a waiting state.
        task1 = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual(task1.get_name(), 'First')
        timer_event = self.workflow.get_tasks_from_spec_name('Event_My_Timer')[0]
        self.assertEqual(TaskState.WAITING, timer_event.state)
