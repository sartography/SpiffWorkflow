from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
from tests.SpiffWorkflow.bpmn.BpmnLoaderForTests import TestUserTaskConverter
from SpiffWorkflow.dmn.serializer import BusinessRuleTaskConverter

class BpmnDmnWorkflowTestCase(BpmnWorkflowTestCase):

    PARSER_CLASS = BpmnDmnParser
    serializer = BpmnWorkflowSerializer.add_task_spec_converter_classes(
        [TestUserTaskConverter, BusinessRuleTaskConverter])