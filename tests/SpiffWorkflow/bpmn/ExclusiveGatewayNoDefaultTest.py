# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.task import Task

__author__ = 'essweine'

class ExclusiveGatewayNoDefaultTest(BpmnWorkflowTestCase):
    """The example bpmn diagram tests both a set cardinality from user input
    as well as looping over an existing array."""

    def setUp(self):
        self.spec = self.load_workflow_spec(
            'exclusive_gateway_no_default.bpmn',
            'NoDefaultGateway')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        first = self.workflow.get_tasks_from_spec_name('StartEvent_1')[0]
        first.data = { 'x': 1 }
        self.assertRaises(WorkflowException, self.workflow.do_engine_steps)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ExclusiveGatewayNoDefaultTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
