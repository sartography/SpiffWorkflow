from SpiffWorkflow.camunda.specs.UserTask import UserTask
from SpiffWorkflow.camunda.parser.UserTaskParser import UserTaskParser
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser, full_tag


class CamundaParser(BpmnParser):
    OVERRIDE_PARSER_CLASSES = {
        full_tag('userTask'): (UserTaskParser, UserTask),
    }


