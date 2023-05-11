# -*- coding: utf-8 -*-
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
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
        self.assertEqual([], self.workflow.get_tasks(TaskState.READY))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.workflow.catch(MessageEventDefinition('Wrong Message'))
        self.assertEqual([], self.workflow.get_tasks(TaskState.READY))
        self.workflow.catch(MessageEventDefinition('Test Message'))
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))

        self.assertEqual('Test Message', self.workflow.get_tasks(TaskState.READY)[0].task_spec.bpmn_name)

        self.workflow.do_engine_steps()
        self.complete_subworkflow()
        self.assertEqual(0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.do_next_exclusive_step('Select Test', choice='Messages')
        self.workflow.do_engine_steps()

        self.save_restore()

        self.assertEqual([], self.workflow.get_tasks(TaskState.READY))
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.workflow.catch(MessageEventDefinition('Wrong Message'))
        self.assertEqual([], self.workflow.get_tasks(TaskState.READY))
        self.workflow.catch(MessageEventDefinition('Test Message'))
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))

        self.save_restore()

        self.workflow.do_engine_steps()
        self.complete_subworkflow()
        self.assertEqual(0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))
