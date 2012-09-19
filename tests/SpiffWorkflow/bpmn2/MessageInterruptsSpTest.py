import unittest
import datetime
import time
from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn2.BpmnWorkflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn2.BpmnWorkflowTestCase import BpmnWorkflowTestCase

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

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.do_next_exclusive_step('Do Something In a Subprocess')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_exclusive_step('Ack Subprocess Done')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughInterruptSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.workflow.accept_message('Test Message')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_exclusive_step('Acknowledge  SP Interrupt Message')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MessageInterruptsSpTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())