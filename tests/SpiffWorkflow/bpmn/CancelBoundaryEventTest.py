# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'michaelc'


class CancelBoundaryTest(BpmnWorkflowTestCase):

    def testInvalidCancelEvent(self):
        self.assertRaises(ValidationException, self.load_workflow_spec, 'message_event.bpmn', 'Process_1dagb7t')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CancelBoundaryTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
