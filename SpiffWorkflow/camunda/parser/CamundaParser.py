from SpiffWorkflow.camunda.specs.UserTask import UserTask
from SpiffWorkflow.camunda.parser.UserTaskParser import UserTaskParser
from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser, full_tag


class CamundaParser(BpmnDmnParser):
    OVERRIDE_PARSER_CLASSES = {F
        full_tag('userTask'): (UserTaskParser, UserTask),
    }


