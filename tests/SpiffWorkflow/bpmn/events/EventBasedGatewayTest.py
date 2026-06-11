from datetime import timedelta

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow, BpmnEvent
from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine, TaskDataEnvironment
from SpiffWorkflow.bpmn.specs.event_definitions import MessageEventDefinition

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

class EventBasedGatewayTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('event-gateway.bpmn', 'Process_0pvx19v')
        self.script_engine = PythonScriptEngine(environment=TaskDataEnvironment({"timedelta": timedelta}))
        self.workflow = BpmnWorkflow(self.spec, script_engine=self.script_engine)

    def testEventBasedGateway(self):
        self.actual_test()

    def testEventBasedGatewaySaveRestore(self):
        self.actual_test(True)

    def actual_test(self, save_restore=False):

        self.workflow.do_engine_steps()
        waiting_tasks = self.workflow.get_tasks(state=TaskState.WAITING)
        if save_restore:
            self.save_restore()
            self.workflow.script_engine = self.script_engine
        self.assertEqual(len(waiting_tasks), 4)
        self.workflow.catch(BpmnEvent(MessageEventDefinition('message_1'), {}))
        self.workflow.do_engine_steps()
        # This needs to be fixed -- it shouldn't be necessary to call this method
        # Unfortunately that requires completely rewriting event based gateways
        # I really don't understand why the bpmn spec dictates that both the gateway and the children
        # have duplicate event definitions, but it sure makes things difficult
        self.assertEqual(self.workflow.is_completed(), True)
        self.assertEqual(self.workflow.get_next_task(spec_name='message_1_event').state, TaskState.COMPLETED)
        self.assertEqual(self.workflow.get_next_task(spec_name='message_2_event').state, TaskState.CANCELLED)
        self.assertEqual(self.workflow.get_next_task(spec_name='timer_event').state, TaskState.CANCELLED)

    def testTimeout(self):

        self.workflow.do_engine_steps()
        waiting_tasks = self.workflow.get_tasks(state=TaskState.WAITING)
        self.assertEqual(len(waiting_tasks), 4)
        timer_event_definition = waiting_tasks[0].task_spec.event_definition.event_definitions[-1]
        self.workflow.catch(BpmnEvent(timer_event_definition))
        self.workflow.do_engine_steps()
        self.assertEqual(self.workflow.is_completed(), True)
        self.assertEqual(self.workflow.get_next_task(spec_name='message_1_event').state, TaskState.CANCELLED)
        self.assertEqual(self.workflow.get_next_task(spec_name='message_2_event').state, TaskState.CANCELLED)
        self.assertEqual(self.workflow.get_next_task(spec_name='timer_event').state, TaskState.COMPLETED)

    def testMultipleStart(self):
        spec, subprocess = self.load_workflow_spec('multiple-start-parallel.bpmn', 'main')
        workflow = BpmnWorkflow(spec)
        workflow.do_engine_steps()
        workflow.catch(BpmnEvent(MessageEventDefinition('message_1'), {}))
        workflow.catch(BpmnEvent(MessageEventDefinition('message_2'), {}))
        workflow.do_engine_steps()
