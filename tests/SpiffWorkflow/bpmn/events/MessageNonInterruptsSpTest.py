from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow, BpmnEvent
from SpiffWorkflow.bpmn.specs.event_definitions import MessageEventDefinition

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class MessageNonInterruptsSpTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec(
            'Test-Workflows/*.bpmn20.xml',
            'sid-b6b1212d-76ea-4ced-888b-a99fbbbca575', 
            False)

    def testRunThroughHappySaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))

        self.do_next_exclusive_step('Do Something In a Subprocess')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_exclusive_step('Ack Subprocess Done')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

    def testRunThroughMessageSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))

        self.workflow.catch(BpmnEvent(MessageEventDefinition('Test Message'), {}))

        self.do_next_named_step('Do Something In a Subprocess')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_named_step('Ack Subprocess Done')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_named_step('Acknowledge SP Parallel Message')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

    def testRunThroughMessageOrder2SaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))

        self.workflow.catch(BpmnEvent(MessageEventDefinition('Test Message'), {}))
        self.do_next_named_step('Do Something In a Subprocess')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_named_step('Acknowledge SP Parallel Message')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_named_step('Ack Subprocess Done')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

    def testRunThroughMessageOrder3SaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))

        self.workflow.catch(BpmnEvent(MessageEventDefinition('Test Message'), {}))

        self.do_next_named_step('Acknowledge SP Parallel Message')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_named_step('Do Something In a Subprocess')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_named_step('Ack Subprocess Done')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
