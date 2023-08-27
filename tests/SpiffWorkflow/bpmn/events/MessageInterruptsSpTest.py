from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.event import BpmnEvent
from SpiffWorkflow.bpmn.specs.event_definitions.message import MessageEventDefinition
from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class MessageInterruptsSpTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec(
            'Test-Workflows/*.bpmn20.xml', 
            'sid-607dfa9b-dbfd-41e8-94f8-42ae37f3b824', 
            False)

    def testRunThroughHappySaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))

        self.do_next_exclusive_step('Do Something In a Subprocess')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_exclusive_step('Ack Subprocess Done')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))

    def testRunThroughInterruptSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))
        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))

        self.workflow.catch(BpmnEvent(MessageEventDefinition('Test Message'), {}))
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_exclusive_step('Acknowledge  SP Interrupt Message')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))
