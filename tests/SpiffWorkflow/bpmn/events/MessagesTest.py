from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow, BpmnEvent
from SpiffWorkflow.bpmn.specs.event_definitions import MessageEventDefinition

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class MessagesTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec(
            'Test-Workflows/*.bpmn20.xml',
            'sid-b0903a88-fe74-4f93-b912-47b815ea8d1c',
            False)

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.do_next_exclusive_step('Select Test', choice='Messages')
        self.workflow.do_engine_steps()
        self.assertEqual([], self.workflow.get_tasks(state=TaskState.READY))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))
        self.workflow.catch(BpmnEvent(MessageEventDefinition('Wrong Message'), {}))
        self.assertEqual([], self.workflow.get_tasks(state=TaskState.READY))
        self.workflow.catch(BpmnEvent(MessageEventDefinition('Test Message'), {}))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))

        self.assertEqual('Test Message', self.workflow.get_tasks(state=TaskState.READY)[0].task_spec.bpmn_name)

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.completed)

    def testRunThroughSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.do_next_exclusive_step('Select Test', choice='Messages')
        self.workflow.do_engine_steps()

        self.save_restore()

        self.assertEqual([], self.workflow.get_tasks(state=TaskState.READY))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.STARTED)))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.WAITING)))
        self.workflow.catch(BpmnEvent(MessageEventDefinition('Wrong Message'), {}))
        self.assertEqual([], self.workflow.get_tasks(state=TaskState.READY))
        self.workflow.catch(BpmnEvent(MessageEventDefinition('Test Message'), {}))
        self.assertEqual(1, len(self.workflow.get_tasks(state=TaskState.READY)))

        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.completed)