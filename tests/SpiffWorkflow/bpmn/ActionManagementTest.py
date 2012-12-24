import unittest
import datetime
import time
from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn.BpmnWorkflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

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
        self.assertEquals('NEW ACTION', self.workflow.get_tasks(Task.READY)[0].get_attribute('script_output'))
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

        overdue_escalation_task = filter(lambda t:t.task_spec.description=='Overdue Escalation', self.workflow.get_tasks())
        self.assertEquals(1, len(overdue_escalation_task))
        overdue_escalation_task = overdue_escalation_task[0]
        self.assertEquals(Task.COMPLETED, overdue_escalation_task.state)
        self.assertEquals('ACTION OVERDUE', overdue_escalation_task.get_attribute('script_output'))

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
        self.assertEquals('ACTION CANCELLED', self.workflow.get_attribute('script_output'))

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
        self.assertEquals('ACTION CANCELLED', self.workflow.get_attribute('script_output'))

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ActionManagementTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())