import unittest
import datetime
import time
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

    def testRunThroughHappySaveAndRestore(self):

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


    def testRunThroughMessageInterruptSaveAndRestore(self):

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


    def testRunThroughHappy(self):

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


    def testRunThroughMessageInterrupt(self):

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

class MessageInterruptsSpTest(WorkflowTest):
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


class MessageNonInterruptsSpTest(WorkflowTest):
    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/*.bpmn20.xml', 'Message Non Interrupt SP')

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

    def testRunThroughMessageSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.workflow.accept_message('Test Message')

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
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughMessageOrder2SaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.workflow.accept_message('Test Message')

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
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughMessageOrder3SaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()

        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.workflow.accept_message('Test Message')

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
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


class MessageNonInterruptTest(WorkflowTest):
    def setUp(self):
        self.spec = self.load_spec()
        #self.spec.dump()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/*.bpmn20.xml', 'Test Workflows')

    def testRunThroughHappySaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()
        self.do_next_exclusive_step('Select Test', choice='Message Non Interrupt')
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


    def testRunThroughMessageInterruptSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()
        self.do_next_exclusive_step('Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.workflow.accept_message('Test Message')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Acknowledge Non-Interrupt Message')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Do Something That Takes A Long Time')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.do_next_exclusive_step('Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.do_next_exclusive_step('Do Something That Takes A Long Time')

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.WAITING)))

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


    def testRunThroughMessageInterrupt(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.do_next_exclusive_step('Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.workflow.accept_message('Test Message')

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Acknowledge Non-Interrupt Message')

        self.workflow.do_engine_steps()
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.do_next_named_step('Do Something That Takes A Long Time')

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughMessageInterruptOtherOrder(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.do_next_exclusive_step('Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.workflow.accept_message('Test Message')

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Do Something That Takes A Long Time')

        self.workflow.do_engine_steps()
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Acknowledge Non-Interrupt Message')

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughMessageInterruptOtherOrderSaveAndRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()
        self.do_next_exclusive_step('Select Test', choice='Message Non Interrupt')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.workflow.accept_message('Test Message')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Do Something That Takes A Long Time')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Acknowledge Non-Interrupt Message')
        self.save_restore()

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

class TimerIntermediateTest(WorkflowTest):
    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/*.bpmn20.xml', 'Timer Intermediate')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)

        due_time = datetime.datetime.now() + datetime.timedelta(seconds=0.5)

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.workflow.get_tasks(Task.READY)[0].set_attribute(due_time=due_time)

        self.workflow.do_engine_steps()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        time.sleep(0.6)

        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.workflow.refresh_waiting_tasks()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))

        self.workflow.do_engine_steps()
        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

class ActionManagementTest(WorkflowTest):
    def setUp(self):
        self.spec = self.load_spec()
        self.workflow = BpmnWorkflow(self.spec)

        start_time = datetime.datetime.now() + datetime.timedelta(seconds=0.5)
        finish_time = datetime.datetime.now() + datetime.timedelta(seconds=1.5)

        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.workflow.get_tasks(Task.READY)[0].set_attribute(start_time=start_time, finish_time=finish_time)

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/*.bpmn20.xml', 'Action Management')

    def testRunThroughHappy(self):
        self.do_next_exclusive_step("Review Action", choice='Approve')
        self.workflow.do_engine_steps()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals('Cancel Action (if necessary)', self.workflow.get_tasks(Task.READY)[0].task_spec.description)

        time.sleep(0.6)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step("Start Work")
        self.workflow.do_engine_steps()

        self.do_next_named_step("Complete Work", choice="Done")
        self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())

    def testRunThroughOverdue(self):
        self.do_next_exclusive_step("Review Action", choice='Approve')
        self.workflow.do_engine_steps()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        self.assertEquals('Cancel Action (if necessary)', self.workflow.get_tasks(Task.READY)[0].task_spec.description)

        time.sleep(0.6)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step("Start Work")
        self.workflow.do_engine_steps()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals('Finish Time', self.workflow.get_tasks(Task.WAITING)[0].task_spec.description)
        time.sleep(1.1)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertNotEquals('Finish Time', self.workflow.get_tasks(Task.WAITING)[0].task_spec.description)


        self.do_next_named_step("Complete Work", choice="Done")
        self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())

    def testRunThroughCancel(self):

        self.do_next_exclusive_step("Review Action", choice='Cancel')
        self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())

    def testRunThroughCancelAfterApproved(self):
        self.do_next_exclusive_step("Review Action", choice='Approve')
        self.workflow.do_engine_steps()

        self.do_next_named_step("Cancel Action (if necessary)")
        self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())

    def testRunThroughCancelAfterWorkStarted(self):
        self.do_next_exclusive_step("Review Action", choice='Approve')
        self.workflow.do_engine_steps()

        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals(1, len(self.workflow.get_tasks(Task.READY)))
        time.sleep(0.6)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step("Start Work")
        self.workflow.do_engine_steps()

        self.do_next_named_step("Cancel Action (if necessary)")
        self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MessagesTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())