# -*- coding: utf-8 -*-



import unittest
import datetime
import time
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
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

        self.assertEqual(1, len(self.workflow.get_tasks(Task.READY)))
        self.workflow.get_tasks(Task.READY)[0].set_data(due_time=due_time)

        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(Task.WAITING)))

        time.sleep(0.6)

        self.assertEqual(1, len(self.workflow.get_tasks(Task.WAITING)))
        self.workflow.refresh_waiting_tasks()
        self.assertEqual(0, len(self.workflow.get_tasks(Task.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(Task.READY)))

        self.workflow.do_engine_steps()
        self.assertEqual(
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TimerIntermediateTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
