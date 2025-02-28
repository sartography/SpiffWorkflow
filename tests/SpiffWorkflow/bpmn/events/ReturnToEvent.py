from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow, BpmnEvent
from SpiffWorkflow.bpmn.specs.event_definitions import MessageEventDefinition

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase


class MessagesTest(BpmnWorkflowTestCase):

    def testEventWaitsAfterLoopback(self):
        spec, subprocesses = self.load_workflow_spec("return_to_event.bpmn", "return_to_event")
        workflow = BpmnWorkflow(spec, subprocesses)
        # Advance to the event
        workflow.do_engine_steps()
        catching_task = workflow.get_next_task(state=TaskState.WAITING)

        # Send the event
        event = BpmnEvent(catching_task.task_spec.event_definition)
        workflow.catch(event)
        workflow.do_engine_steps()

        task = workflow.get_next_task(state=TaskState.READY)
        self.assertEqual(task.task_spec.name, 'manual')
        task.data['repeat'] = True
        task.run()
        workflow.do_engine_steps()

        # When we return, the previous event should be cleared and we should wait again
        catching_task = workflow.get_next_task(state=TaskState.WAITING)
        self.assertEqual(catching_task.task_spec.name, 'Event_10ncvxn')

