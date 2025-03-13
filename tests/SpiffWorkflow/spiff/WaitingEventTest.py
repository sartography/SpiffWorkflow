from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow, BpmnEvent

from .BaseTestCase import BaseTestCase


class WaitingEventTest(BaseTestCase):

    def test_data_persists_through_call_activity(self):

        spec, subprocesses = self.load_workflow_spec('waiting_event.bpmn', 'main')
        workflow = BpmnWorkflow(spec, subprocesses)
        workflow.do_engine_steps()
        events = workflow.waiting_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].correlations, {'MainCorrelationKey': {'uid': 1}})

        task = workflow.get_next_task(state=TaskState.WAITING)
        payload = {'uid': 1, 'data': 'asdf'},
        event = BpmnEvent(task.task_spec.event_definition, payload, events[0].correlations)
        workflow.send_event(event)
        workflow.do_engine_steps()
        self.assertTrue(workflow.completed)
        self.assertTrue(workflow.data, {'a_var': payload})
