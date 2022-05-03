# -*- coding: utf-8 -*-



import unittest
import datetime
import time
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class MessageNonInterruptsSpTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/*.bpmn20.xml', 'Message Non Interrupt SP')

    def testRunThroughHappySaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.do_next_exclusive_step('Do Something In a Subprocess')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_exclusive_step('Ack Subprocess Done')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughMessageSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.workflow.message('Test Message')

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
        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughMessageOrder2SaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.workflow.message('Test Message')

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
        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughMessageOrder3SaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.workflow.message('Test Message')

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
        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MessageNonInterruptsSpTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
