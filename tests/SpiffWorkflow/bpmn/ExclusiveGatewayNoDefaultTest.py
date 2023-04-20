# -*- coding: utf-8 -*-
import unittest

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.task import TaskState

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'essweine'

class ExclusiveGatewayNoDefaultTest(BpmnWorkflowTestCase):
    """The example bpmn diagram tests both a set cardinality from user input
    as well as looping over an existing array."""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('exclusive_gateway_no_default.bpmn', 'NoDefaultGateway')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):

        first = self.workflow.get_tasks_from_spec_name('StartEvent_1')[0]
        first.data = { 'x': 1 }
        self.assertRaises(WorkflowException, self.workflow.do_engine_steps)
        task = self.workflow.get_tasks_from_spec_name('Gateway_CheckValue')[0]
        self.assertEqual(task.state, TaskState.ERROR)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ExclusiveGatewayNoDefaultTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
