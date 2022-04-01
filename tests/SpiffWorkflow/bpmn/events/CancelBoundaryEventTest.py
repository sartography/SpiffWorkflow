# -*- coding: utf-8 -*-



import unittest
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'michaelc'


class CancelBoundaryTest(BpmnWorkflowTestCase):

    def testInvalidCancelEvent(self):
        self.assertRaises(ValidationException, self.load_workflow_spec, 'invalid_cancel.bpmn', 'Process_1dagb7t')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CancelBoundaryTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
