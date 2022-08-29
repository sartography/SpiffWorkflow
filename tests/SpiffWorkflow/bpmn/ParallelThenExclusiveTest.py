# -*- coding: utf-8 -*-

import unittest
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class ParallelThenExclusiveTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('Test-Workflows/Parallel-Then-Exclusive.bpmn20.xml', 'Parallel Then Exclusive')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughParallelTaskFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughChoiceFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughChoiceThreadCompleteFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))


class ParallelThenExclusiveNoInclusiveTest(ParallelThenExclusiveTest):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-Then-Exclusive-No-Inclusive.bpmn20.xml', 
            'Parallel Then Exclusive No Inclusive')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()


def suite():
    return unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
