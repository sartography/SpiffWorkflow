# -*- coding: utf-8 -*-

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'essweine'


class InvalidProcessIDTest(BpmnWorkflowTestCase):

    def testInvalidWorkflowProcess(self):
        self.assertRaisesRegex(
            Exception, "The process '\w+' was not found*",
            self.load_workflow_spec, "invalid_process*.bpmn", "topworkflow")

    def testInvalidCalledElement(self):
        self.assertRaisesRegex(
            ValidationException, "The process '\w+' was not found",
            self.load_workflow_spec, "invalid_process*.bpmn", "top_workflow")

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(InvalidProcessIDTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
