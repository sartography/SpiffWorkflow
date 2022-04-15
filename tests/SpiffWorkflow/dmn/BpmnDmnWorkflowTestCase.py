from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
from tests.SpiffWorkflow.bpmn.BpmnLoaderForTests import TestUserTaskConverter
from SpiffWorkflow.dmn.serializer import BusinessRuleTaskConverter

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter([BusinessRuleTaskConverter])


class BpmnDmnWorkflowTestCase(BpmnWorkflowTestCase):

    PARSER_CLASS = BpmnDmnParser
    serializer = BpmnWorkflowSerializer(wf_spec_converter)