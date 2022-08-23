# -*- coding: utf-8 -*-

import unittest
import datetime
import time
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class TimerIntermediateTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesss = self.load_workflow_spec('Test-Workflows/Timer-Intermediate.bpmn20.xml', 'Timer Intermediate')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesss)

    def testRunThroughHappy(self):

        due_time = datetime.datetime.now() + datetime.timedelta(seconds=0.01)

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.workflow.get_tasks(TaskState.READY)[0].set_data(due_time=due_time)

        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))

        time.sleep(0.02)

        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.workflow.refresh_waiting_tasks()
        self.assertEqual(0, len(self.workflow.get_tasks(TaskState.WAITING)))
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))

        self.workflow.do_engine_steps()
        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TimerIntermediateTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
