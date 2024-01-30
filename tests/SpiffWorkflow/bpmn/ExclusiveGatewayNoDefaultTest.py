import unittest

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.exceptions import WorkflowException

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'essweine'

class ExclusiveGatewayNoDefaultTest(BpmnWorkflowTestCase):
    """The example bpmn diagram tests both a set cardinality from user input
    as well as looping over an existing array."""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('exclusive_gateway_no_default.bpmn', 'NoDefaultGateway')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):

        first = self.workflow.get_next_task(end_at_spec='StartEvent_1')
        first.data = { 'x': 1 }
        self.assertRaises(WorkflowException, self.workflow.do_engine_steps)
        task = self.workflow.get_next_task(spec_name='Gateway_CheckValue')
        self.assertEqual(task.state, TaskState.ERROR)
