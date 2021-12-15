from ..specs.UserTask import UserTask
from ..parser.UserTaskParser import UserTaskParser
from ...bpmn.parser.BpmnParser import BpmnParser, full_tag


class CamundaParser(BpmnParser):
    OVERRIDE_PARSER_CLASSES = {
        full_tag('userTask'): (UserTaskParser, UserTask),
    }


