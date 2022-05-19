# -*- coding: utf-8 -*-

import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class LoopTaskTest(BpmnWorkflowTestCase):
    """The example bpmn diagram has a single task with a loop cardinality of 5.
    It should repeat 5 times before termination."""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('bpmnLoopTask.bpmn','LoopTaskTest')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):

        for i in range(5):
            self.workflow.do_engine_steps()
            ready_tasks = self.workflow.get_ready_user_tasks()
            self.assertTrue(len(ready_tasks) ==1)
            self.assertTrue(ready_tasks[0].task_spec.is_loop_task())
            self.assertFalse(self.workflow.is_completed())
            last_task = self.workflow.last_task

            self.do_next_exclusive_step('Activity_TestLoop')

        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertTrue(len(ready_tasks) ==1)
        ready_tasks[0].terminate_loop()
        self.do_next_exclusive_step('Activity_TestLoop')
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())


    def testSaveRestore(self):

        for i in range(5):
            self.save_restore()
            self.workflow.do_engine_steps()
            ready_tasks = self.workflow.get_ready_user_tasks()
            self.assertTrue(len(ready_tasks) ==1)
            self.assertTrue(ready_tasks[0].task_spec.is_loop_task())
            self.assertFalse(self.workflow.is_completed())
            self.do_next_exclusive_step('Activity_TestLoop')

        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertTrue(len(ready_tasks) ==1)
        ready_tasks[0].terminate_loop()
        self.do_next_exclusive_step('Activity_TestLoop')
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(LoopTaskTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
