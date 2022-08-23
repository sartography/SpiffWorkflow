# -*- coding: utf-8 -*-

import unittest
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class ParallelFromCamunda(BpmnWorkflowTestCase):

    # Should we move this to the Camunda package?  Is this even testing anything Camunda related?

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('Test-Workflows/Parallel.camunda.bpmn20.xml', 'Process_1hb021r')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughParallelTaskFirst(self):

        # 1 first task
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.do_next_named_step('First Task')
        self.save_restore()
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')

        # 3 parallel tasks
        self.assertEqual(3, len(self.workflow.get_tasks(TaskState.READY)))
        self.do_next_named_step('Parallel Task A')
        self.save_restore()
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Parallel Task B')
        self.save_restore()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Parallel Task C')
        self.save_restore()
        self.workflow.do_engine_steps()
        self.save_restore()

        # 1 last task
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.do_next_named_step('Last Task')
        self.save_restore()
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')

    def testAllParallelDataMakesItIntoGatewayTask(self):
        """It should be true that data collected across parallel tasks
        is all available in the join task."""

        self.do_next_named_step('First Task')
        self.do_next_named_step('Parallel Task A',
                                set_attribs={"taskA": "taskA"})
        self.do_next_named_step('Parallel Task B',
                                set_attribs={"taskB": "taskB"})
        self.do_next_named_step('Parallel Task C',
                                set_attribs={"taskC": "taskC"})
        self.workflow.do_engine_steps()
        self.do_next_named_step('Last Task')
        self.assertEqual("taskA", self.workflow.last_task.data["taskA"])
        self.assertEqual("taskB", self.workflow.last_task.data["taskB"])
        self.assertEqual("taskC", self.workflow.last_task.data["taskC"])


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ParallelFromCamunda)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
