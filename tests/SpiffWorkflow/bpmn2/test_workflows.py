import unittest
from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn2.BpmnWorkflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn2.workflow1 import WorkflowTest

__author__ = 'matth'


class MessagesTest(WorkflowTest):
    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/*.bpmn20.xml', 'Test Workflows')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.do_next_exclusive_step('Select Test', choice='Messages')
        self.workflow.do_engine_steps()
        self.assertEquals([], self.workflow.get_tasks(Task.READY))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.workflow.accept_message('Wrong Message')
        self.assertEquals([], self.workflow.get_tasks(Task.READY))
        self.workflow.accept_message('Test Message')
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))

        self.assertEquals('Test Message', self.workflow.get_tasks(Task.READY)[0].task_spec.description)

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.do_next_exclusive_step('Select Test', choice='Messages')
        self.workflow.do_engine_steps()

        self.save_restore()

        self.assertEquals([], self.workflow.get_tasks(Task.READY))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.workflow.accept_message('Wrong Message')
        self.assertEquals([], self.workflow.get_tasks(Task.READY))
        self.workflow.accept_message('Test Message')

        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))



class MessageInterruptsTest(WorkflowTest):
    def setUp(self):
        self.spec = self.load_spec()
        #self.spec.dump()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/*.bpmn20.xml', 'Test Workflows')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()
        self.do_next_exclusive_step('Select Test', choice='Message Interrupts')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.do_next_exclusive_step('Do Something That Takes A Long Time')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.WAITING)))

        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


    def testRunThroughMessageInterrupt(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()
        self.do_next_exclusive_step('Select Test', choice='Message Interrupts')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.workflow.accept_message('Test Message')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_exclusive_step('Acknowledge Interrupt Message')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


    def testRunThroughHappySaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.do_next_exclusive_step('Select Test', choice='Message Interrupts')
        self.workflow.do_engine_steps()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.do_next_exclusive_step('Do Something That Takes A Long Time')

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.WAITING)))

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


    def testRunThroughMessageInterruptSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.do_next_exclusive_step('Select Test', choice='Message Interrupts')
        self.workflow.do_engine_steps()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.workflow.accept_message('Test Message')

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_exclusive_step('Acknowledge Interrupt Message')

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ScriptsTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())