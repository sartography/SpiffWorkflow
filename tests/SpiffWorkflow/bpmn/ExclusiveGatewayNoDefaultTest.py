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
__author__ = 'matth'

from tests.SpiffWorkflow.camunda.BaseTestCase import BaseTestCase


class ExclusiveGatewayNoDefaultTest(BaseTestCase):
    """The example bpmn diagram tests both a set cardinality from user input
    as well as looping over an existing array."""

    def setUp(self):
        self.spec = self.load_workflow_spec(
            'data/exclusive_gateway_default.bpmn',
            'NoDefaultGateway')

    def testRunThroughHappy(self):
        self.workflow = BpmnWorkflow(self.spec)
        first = self.workflow.get_tasks_from_spec_name('StartEvent_1')
        first.data = { 'x': 1 }
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ExclusiveGatewayNoDefaultTest())

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
