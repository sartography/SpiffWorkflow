from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.task import TaskState
from .BpmnWorkflowTestCase import BpmnWorkflowTestCase


class ResetTokenOnBoundaryEventTest(BpmnWorkflowTestCase):
    """Assure that when we reset a token to a previous task, and that
    task has a boundary event, that the boundary event is reset to the
    correct state."""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('reset_with_boundary_event.bpmn', 'token')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testResetToOuterWorkflow(self):
        self.reset_to_outer_workflow(save_restore=False)

    def testResetToSubprocess(self):
        self.reset_to_subprocess(save_restore=False)

    def testSaveRestore(self):
        self.reset_to_outer_workflow(save_restore=True)

    def reset_to_outer_workflow(self, save_restore=False):

        # Advance insie the subworkflow
        self.advance_to_task('Last')
        sub = self.workflow.get_tasks_from_spec_name('subprocess')[0]
        timer_event = self.workflow.get_tasks_from_spec_name('Event_My_Timer')[0]
        self.assertEqual(TaskState.CANCELLED, timer_event.state)

        if save_restore:
            self.save_restore()

        # Here we reset back to the first task
        first = self.workflow.get_tasks_from_spec_name('First')[0]
        self.workflow.reset_from_task_id(first.id)

        if save_restore:
            self.save_restore()

        # At which point, the timer event should return to a waiting state, the subprocess shoud have been removed
        task = self.workflow.get_tasks_from_spec_name('First')[0]
        self.assertEqual(task.state, TaskState.READY)
        timer_event = self.workflow.get_tasks_from_spec_name('Event_My_Timer')[0]
        self.assertEqual(timer_event.state, TaskState.WAITING)
        self.assertNotIn(sub.id, self.workflow.subprocesses)

        # Ensure the workflow can be completed without being stuck on stranded tasks
        self.complete_workflow()
        self.assertTrue(self.workflow.is_completed())

    def reset_to_subprocess(self, save_restore=False):

        # Advance past the subworkflow
        self.advance_to_task('Final')
        if save_restore:
            self.save_restore()

        # Reset to a task inside the subworkflow
        task = self.workflow.get_tasks_from_spec_name('Last')[0]
        self.workflow.reset_from_task_id(task.id)

        if save_restore:
            self.save_restore()

        # The task we returned to should be ready, the subprocess should be waiting, the final task should be future
        sub = self.workflow.get_tasks_from_spec_name('subprocess')[0]
        self.assertEqual(sub.state, TaskState.WAITING)
        self.assertEqual(task.state, TaskState.READY)
        final = self.workflow.get_tasks_from_spec_name('Final')[0]
        self.assertEqual(final.state, TaskState.FUTURE)

        # Ensure the workflow can be completed without being stuck on stranded tasks        
        self.complete_workflow()
        self.assertTrue(self.workflow.is_completed())

    def advance_to_task(self, name):

        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(task_filter=self.ready_task_filter)
        while ready_tasks[0].task_spec.name != name:
            ready_tasks[0].run()
            self.workflow.do_engine_steps()
            self.workflow.refresh_waiting_tasks()
            ready_tasks = self.workflow.get_tasks(task_filter=self.ready_task_filter)

    def complete_workflow(self):

        ready_tasks = self.workflow.get_tasks(task_filter=self.ready_task_filter)
        while len(ready_tasks) > 0:
            ready_tasks[0].run()
            self.workflow.do_engine_steps()
            self.workflow.refresh_waiting_tasks()
            ready_tasks = self.workflow.get_tasks(task_filter=self.ready_task_filter)
