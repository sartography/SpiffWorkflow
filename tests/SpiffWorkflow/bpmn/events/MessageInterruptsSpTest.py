from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow, BpmnEvent
from SpiffWorkflow.bpmn.specs.event_definitions import MessageEventDefinition

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

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.assertEqual(2, len(self.workflow.get_tasks(state=TaskState.WAITING)))

        self.do_next_exclusive_step('Do Something In a Subprocess')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_exclusive_step('Ack Subprocess Done')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(state=TaskState.READY|TaskState.WAITING)))

    def testRunThroughInterruptSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.assertEqual(2, len(self.workflow.get_tasks(state=TaskState.WAITING)))

        self.workflow.catch(BpmnEvent(MessageEventDefinition('Test Message'), {}))
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_exclusive_step('Acknowledge  SP Interrupt Message')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(state=TaskState.READY|TaskState.WAITING)))
