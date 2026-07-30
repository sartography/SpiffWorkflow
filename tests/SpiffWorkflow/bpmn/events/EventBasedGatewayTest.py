from datetime import timedelta
from time import sleep

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow, BpmnEvent
from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine, TaskDataEnvironment
from SpiffWorkflow.bpmn.specs.event_definitions import MessageEventDefinition
from SpiffWorkflow.spiff.specs.event_definitions import MessageEventDefinition as SpiffMessageEventDefinition

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

class EventBasedGatewayTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('event-gateway.bpmn', 'Process_0pvx19v')
        self.script_engine = PythonScriptEngine(environment=TaskDataEnvironment({"timedelta": timedelta}))
        self.workflow = BpmnWorkflow(self.spec, script_engine=self.script_engine)
        self.workflow.do_engine_steps()

    def testEventBasedGateway(self):
        self.actual_test()

    def testEventBasedGatewaySaveRestore(self):
        self.actual_test(True)

    def testMessagePayloadUsesConfiguredEventDefinition(self):
        gateway_task = self.workflow.get_tasks(state=TaskState.WAITING)[0]
        event_definitions = gateway_task.task_spec.event_definition.event_definitions
        message_idx = next(idx for idx, event_definition in enumerate(event_definitions) if event_definition.name == 'message_2')
        event_definitions[message_idx] = SpiffMessageEventDefinition('message_2', message_var='result')

        self.workflow.catch(
            BpmnEvent(SpiffMessageEventDefinition('message_2'), {'message': 'message 2'})
        )
        self.workflow.do_engine_steps()

        message_task = self.workflow.get_next_task(spec_name='message_2_event')
        self.assertEqual(message_task.data['result'], {'message': 'message 2'})

    def actual_test(self, save_restore=False):

        waiting_tasks = self.workflow.get_tasks(state=TaskState.WAITING)
        if save_restore:
            self.save_restore()
            self.workflow.script_engine = self.script_engine
        self.assertEqual(len(waiting_tasks), 1)
        self.workflow.catch(BpmnEvent(MessageEventDefinition('message_2'), {'result': 'message 2'}))
        self.workflow.do_engine_steps()
        self.assertEqual(self.workflow.is_completed(), True)
        message_task = self.workflow.get_next_task(spec_name='message_2_event')
        self.assertEqual(message_task.state, TaskState.COMPLETED)
        self.assertEqual(message_task.data['result'], 'message 2')
        # The gateway now drops the branches that weren't followed, so these tasks shouldn't exist
        self.assertEqual(self.workflow.get_next_task(spec_name='message_1_event'), None)
        self.assertEqual(self.workflow.get_next_task(spec_name='timer_event'), None)

    def testLoop(self):

        self.workflow.catch(BpmnEvent(MessageEventDefinition('message_1'), {}))
        self.workflow.do_engine_steps()
        # We should have returned to the gateway, with one completed message 1 task and three maybe tasks
        waiting_tasks = self.workflow.get_tasks(state=TaskState.WAITING)
        self.assertEqual(len(waiting_tasks), 1)
        states = [t.state for t in self.workflow.get_tasks(spec_name='message_1_event')]
        self.assertEqual(states, [TaskState.COMPLETED, TaskState.MAYBE])
        self.assertEqual(self.workflow.get_next_task(spec_name='message_2_event').state, TaskState.MAYBE)
        self.assertEqual(self.workflow.get_next_task(spec_name='timer_event').state, TaskState.MAYBE)

    def testTimeout(self):

        self.workflow.do_engine_steps()
        waiting_tasks = self.workflow.get_tasks(state=TaskState.WAITING)
        self.assertEqual(len(waiting_tasks), 1)
        sleep(0.3)
        self.workflow.refresh_timers()
        # The gateway should be ready now
        task = self.workflow.get_next_task(state=TaskState.READY)
        self.assertEqual(task.state, TaskState.READY)
        self.workflow.do_engine_steps()
        self.assertEqual(self.workflow.is_completed(), True)
        self.assertEqual(self.workflow.get_next_task(spec_name='message_1_event'), None)
        self.assertEqual(self.workflow.get_next_task(spec_name='message_2_event'), None)
        self.assertEqual(self.workflow.get_next_task(spec_name='timer_event').state, TaskState.COMPLETED)

    def testMultipleStart(self):
        spec, subprocess = self.load_workflow_spec('multiple-start-parallel.bpmn', 'main')
        workflow = BpmnWorkflow(spec)
        workflow.do_engine_steps()
        workflow.catch(BpmnEvent(MessageEventDefinition('message_1'), {}))
        workflow.catch(BpmnEvent(MessageEventDefinition('message_2'), {}))
        workflow.do_engine_steps()
