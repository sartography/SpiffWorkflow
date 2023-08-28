# -*- coding: utf-8 -*-

import unittest

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase


class ParallelOrderTest(BpmnWorkflowTestCase):
    """The example bpmn diagram has a 4 parallel workflows, this
    verifies that the parallel tasks have a natural order that follows
    the visual layout of the diagram, rather than just the order in which
    they were created. """

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('ParallelOrder.bpmn','ParallelOrder')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):

        self.workflow.do_engine_steps()
        self.assertFalse(self.workflow.is_completed())
        self.assertEqual(4, len(self.get_ready_user_tasks()))
        tasks = self.get_ready_user_tasks()
        self.assertEquals("Task 1", tasks[0].task_spec.bpmn_name)
        self.assertEquals("Task 2", tasks[1].task_spec.bpmn_name)
        self.assertEquals("Task 3", tasks[2].task_spec.bpmn_name)
        self.assertEquals("Task 4", tasks[3].task_spec.bpmn_name)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ParallelOrderTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
