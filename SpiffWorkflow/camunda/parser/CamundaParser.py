from ..specs.UserTask import UserTask
from ..parser.UserTaskParser import UserTaskParser
from ...bpmn.parser.BpmnParser import full_tag

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.dmn.specs.BusinessRuleTask import BusinessRuleTask
from SpiffWorkflow.camunda.parser.business_rule_task import BusinessRuleTaskParser


class CamundaParser(BpmnDmnParser):

    OVERRIDE_PARSER_CLASSES = {
        full_tag('userTask'): (UserTaskParser, UserTask),
        full_tag('businessRuleTask'): (BusinessRuleTaskParser, BusinessRuleTask),
    }
