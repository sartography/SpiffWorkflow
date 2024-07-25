from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow, BpmnEvent
from SpiffWorkflow.bpmn.specs.event_definitions import MessageEventDefinition

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

class StartEventSplitTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocess_specs = self.load_workflow_spec('start_event_split.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec)

    def test_start_event_split(self):
        self.actual_test()

    def test_start_event_split_save_restore(self):
        self.actual_test(True)

    def actual_test(self, save_restore=False):

        ready = self.workflow.get_next_task(state=TaskState.READY)
        self.run_until_input_required()

        if save_restore:
            self.save_restore()

        start_1 = self.workflow.get_next_task(spec_name='start_1')
        start_2 = self.workflow.get_next_task(spec_name='start_2')
        self.assertEqual(start_1.state, TaskState.WAITING)
        self.assertEqual(start_2.state, TaskState.WAITING)

        message = BpmnEvent(MessageEventDefinition('message_1'))
        self.workflow.catch(message)
        self.run_until_input_required()

        self.assertEqual(start_1.state, TaskState.COMPLETED)
        self.assertEqual(start_2.state, TaskState.CANCELLED)

        any_task = self.workflow.get_next_task(spec_name='any_task')
        self.assertEqual(any_task.state, TaskState.READY)
        any_task.run()

        self.run_until_input_required()
        self.assertTrue(self.workflow.completed)


