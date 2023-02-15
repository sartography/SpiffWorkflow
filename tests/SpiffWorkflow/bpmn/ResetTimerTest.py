
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.task import TaskState

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

class ResetTimerTest(BpmnWorkflowTestCase):

    def test_timer(self):
        spec, subprocess = self.load_workflow_spec('reset_timer.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec, subprocess)
        self.workflow.do_engine_steps()
        task_1 = self.workflow.get_tasks_from_spec_name('task_1')[0]
        timer = self.workflow.get_tasks_from_spec_name('timer')[0]
        original_timer = timer.internal_data.get('event_value')
        # This returns us to the task
        task_1.data['modify'] = True
        task_1.complete()
        self.workflow.do_engine_steps()
        # The timer should be waiting and the time should have been updated
        self.assertEqual(task_1.state, TaskState.READY)
        self.assertEqual(timer.state, TaskState.WAITING)
        self.assertGreater(timer.internal_data.get('event_value'), original_timer)
        task_1.data['modify'] = False
        task_1.complete()
        self.workflow.do_engine_steps()
        self.assertEqual(timer.state, TaskState.CANCELLED)
        self.assertTrue(self.workflow.is_completed())