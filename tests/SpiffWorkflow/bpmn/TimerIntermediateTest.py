import unittest
import datetime
import time
from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn.BpmnWorkflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class TimerIntermediateTest(BpmnWorkflowTestCase):
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

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TimerIntermediateTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())