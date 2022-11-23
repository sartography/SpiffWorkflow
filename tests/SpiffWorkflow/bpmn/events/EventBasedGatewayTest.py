from datetime import timedelta

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.specs.events.event_definitions import MessageEventDefinition
from SpiffWorkflow.task import TaskState

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

class EventBsedGatewayTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('event-gateway.bpmn', 'Process_0pvx19v')
        self.script_engine = PythonScriptEngine(default_globals={"timedelta": timedelta})
        self.workflow = BpmnWorkflow(self.spec, script_engine=self.script_engine)

    def testEventBasedGateway(self):
        self.actual_test()

    def testEventBasedGatewaySaveRestore(self):
        self.actual_test(True)
    
    def actual_test(self, save_restore=False):

        self.workflow.do_engine_steps()
        waiting_tasks = self.workflow.get_waiting_tasks()
        if save_restore:
            self.save_restore()
            self.workflow.script_engine = self.script_engine
        self.assertEqual(len(waiting_tasks), 1)
        self.workflow.catch(MessageEventDefinition('message_1'))
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEqual(self.workflow.is_completed(), True)
        self.assertEqual(self.workflow.get_tasks_from_spec_name('message_1_event')[0].state, TaskState.COMPLETED)
        self.assertEqual(self.workflow.get_tasks_from_spec_name('message_2_event')[0].state, TaskState.CANCELLED)
        self.assertEqual(self.workflow.get_tasks_from_spec_name('timer_event')[0].state, TaskState.CANCELLED)