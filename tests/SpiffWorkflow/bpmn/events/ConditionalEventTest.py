from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

class ConditionalEventTest(BpmnWorkflowTestCase):

    def testIntermediateEvent(self):
        spec, subprocesses = self.load_workflow_spec('conditional_event.bpmn', 'intermediate')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()
        b = self.workflow.get_next_task(spec_name='task_b')
        b.run()
        self.save_restore()
        event = self.workflow.get_next_task(spec_name='event_1')
        # The event waits for task_a_done to become True
        self.assertEqual(event.state, TaskState.WAITING)
        a = self.workflow.get_next_task(spec_name='task_a')
        a.data['task_a_done'] = True
        a.run()
        self.save_restore()
        # Completion of A results in event being updated
        self.assertEqual(event.state, TaskState.READY)
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.completed)

    def testBoundaryEvent(self):
        spec, subprocesses = self.load_workflow_spec('conditional_event.bpmn', 'boundary')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()
        c = self.workflow.get_next_task(spec_name='task_c')
        c.data['task_c_done'] = True
        event = self.workflow.get_next_task(spec_name='event_2')
        self.assertEqual(event.state, TaskState.WAITING)
        c.run()
        self.assertEqual(event.state, TaskState.READY)
        self.workflow.do_engine_steps()
        d = self.workflow.get_next_task(spec_name='task_d')
        self.assertEqual(d.state, TaskState.CANCELLED)
        self.assertTrue(self.workflow.completed)

