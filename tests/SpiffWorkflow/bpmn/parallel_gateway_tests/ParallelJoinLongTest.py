# -*- coding: utf-8 -*-

import unittest
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class ParallelJoinLongTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('Test-Workflows/Parallel-Join-Long.bpmn20.xml', 'Parallel Join Long')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughAlternating(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step(
            'Thread 1 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()
        self.do_next_named_step(
            'Thread 2 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()

        for i in range(1, 13):
            self.do_next_named_step(
                'Thread 1 - Task %d' % i, with_save_load=True)
            self.workflow.do_engine_steps()
            self.do_next_named_step(
                'Thread 2 - Task %d' % i, with_save_load=True)
            self.workflow.do_engine_steps()

        self.do_next_named_step('Done', with_save_load=True)
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughThread1First(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step(
            'Thread 1 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()
        for i in range(1, 13):
            self.do_next_named_step('Thread 1 - Task %d' % i)
            self.workflow.do_engine_steps()

        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.do_next_named_step(
            'Thread 2 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()
        for i in range(1, 13):
            self.do_next_named_step(
                'Thread 2 - Task %d' % i, with_save_load=True)
            self.workflow.do_engine_steps()

        self.do_next_named_step('Done', with_save_load=True)
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ParallelJoinLongTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
