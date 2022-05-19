import unittest
import datetime
import time
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'neilc'


class NestedProcessesTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('Test-Workflows/Nested*.bpmn20.xml', 'Nested Subprocesses')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):

        self.do_next_named_step('Action1')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.do_next_named_step('Action2')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.do_next_named_step('Action3')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NestedProcessesTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
