from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow, BpmnEvent
from SpiffWorkflow.bpmn.specs.event_definitions import MessageEventDefinition

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class MessageInterruptsTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec(
            'Test-Workflows/*.bpmn20.xml', 
            'sid-b0903a88-fe74-4f93-b912-47b815ea8d1c',
            False)

    def testRunThroughHappySaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()
        self.do_next_exclusive_step('Select Test', choice='Message Interrupts')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))

        self.do_next_exclusive_step('Do Something That Takes A Long Time')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(state=TaskState.WAITING)))

        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

    def testRunThroughMessageInterruptSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()
        self.do_next_exclusive_step('Select Test', choice='Message Interrupts')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))

        self.workflow.catch(BpmnEvent(MessageEventDefinition('Test Message'), {}))
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))

        self.do_next_exclusive_step('Acknowledge Interrupt Message')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertTrue(self.workflow.is_completed())

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.do_next_exclusive_step('Select Test', choice='Message Interrupts')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))

        self.do_next_exclusive_step('Do Something That Takes A Long Time')

        self.workflow.do_engine_steps()
        self.assertEqual(0, len(self.workflow.get_tasks(state=TaskState.WAITING)))

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

    def testRunThroughMessageInterrupt(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.do_next_exclusive_step('Select Test', choice='Message Interrupts')
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))

        self.workflow.catch(BpmnEvent(MessageEventDefinition('Test Message'), {}))

        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))

        self.do_next_exclusive_step('Acknowledge Interrupt Message')

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
