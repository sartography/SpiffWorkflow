import unittest
import datetime
import time
from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn2.BpmnWorkflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn2.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class ActionManagementTest(BpmnWorkflowTestCase):
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
    return unittest.TestLoader().loadTestsFromTestCase(ActionManagementTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())