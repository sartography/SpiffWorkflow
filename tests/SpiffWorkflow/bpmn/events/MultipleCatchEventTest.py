from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.event import BpmnEvent
from SpiffWorkflow.bpmn.specs.event_definitions.message import MessageEventDefinition

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase


class MultipleStartEventTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('multiple-start.bpmn', 'main')
        self.workflow = BpmnWorkflow(self.spec)

    def testMultipleStartEvent(self):
        self.actual_test()

    def testMultipleStartEventSaveRestore(self):
        self.actual_test(True)
    
    def actual_test(self, save_restore=False):

        self.workflow.do_engine_steps()
        waiting_tasks = self.workflow.get_waiting_tasks()

        if save_restore:
            self.save_restore()

        # The start event should be waiting
        self.assertEqual(len(waiting_tasks), 1)
        self.assertEqual(waiting_tasks[0].task_spec.name, 'StartEvent_1')

        self.workflow.catch(BpmnEvent(MessageEventDefinition('message_1'), {}))
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()

        # Now the first task should be ready
        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 1)
        self.assertEqual(ready_tasks[0].task_spec.name, 'any_task')


class ParallelStartEventTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('multiple-start-parallel.bpmn', 'main')
        self.workflow = BpmnWorkflow(self.spec)

    def testParallelStartEvent(self):
        self.actual_test()

    def testParallelStartEventSaveRestore(self):
        self.actual_test(True)
    
    def actual_test(self, save_restore=False):

        self.workflow.do_engine_steps()
        waiting_tasks = self.workflow.get_waiting_tasks()

        if save_restore:
            self.save_restore()

        # The start event should be waiting
        self.assertEqual(len(waiting_tasks), 1)
        self.assertEqual(waiting_tasks[0].task_spec.name, 'StartEvent_1')

        self.workflow.catch(BpmnEvent(MessageEventDefinition('message_1'), {}))
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()

        # It should still be waiting because it has to receive both messages
        waiting_tasks = self.workflow.get_waiting_tasks()
        self.assertEqual(len(waiting_tasks), 1)
        self.assertEqual(waiting_tasks[0].task_spec.name, 'StartEvent_1')

        self.workflow.catch(BpmnEvent(MessageEventDefinition('message_2'), {}))
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()

        # Now the first task should be ready
        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 1)
        self.assertEqual(ready_tasks[0].task_spec.name, 'any_task')
