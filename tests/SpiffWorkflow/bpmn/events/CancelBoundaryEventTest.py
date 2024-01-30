from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'michaelc'


class CancelBoundaryTest(BpmnWorkflowTestCase):

    def testInvalidCancelEvent(self):
        self.assertRaises(ValidationException, self.load_workflow_spec, 'invalid_cancel.bpmn', 'Process_1dagb7t')

