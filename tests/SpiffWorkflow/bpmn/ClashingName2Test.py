# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
__author__ = 'kellym'



class ClashingNameTest2(BpmnWorkflowTestCase):
    """The example bpmn diagram tests both a set cardinality from user input
    as well as looping over an existing array."""

    def setUp(self):
        pass
    def loadWorkflow(self):
        self.spec = self.load_workflow_spec(
            'Approvals_bad.bpmn',
            'Approvals')
    def testRunThroughHappy(self):
        # make sure we raise an exception
        # when validating a workflow with multiple
        # same IDs in the BPMN workspace
        self.assertRaises(ValidationException,self.loadWorkflow)



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ClashingNameTest2)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
