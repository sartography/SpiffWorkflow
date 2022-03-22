# -*- coding: utf-8 -*-



import unittest
import datetime
import time
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class MessageInterruptsSpTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/*.bpmn20.xml', 'Message Interrupts SP')

    def testRunThroughHappySaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.do_next_exclusive_step('Do Something In a Subprocess')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_exclusive_step('Ack Subprocess Done')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughInterruptSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEqual(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.workflow.message('Test Message')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_exclusive_step('Acknowledge  SP Interrupt Message')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEqual(
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MessageInterruptsSpTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
