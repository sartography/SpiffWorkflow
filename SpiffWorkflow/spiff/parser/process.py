from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.bpmn.parser.BpmnParser import full_tag

from SpiffWorkflow.spiff.specs import NoneTask, ManualTask, UserTask
from SpiffWorkflow.spiff.specs import SubWorkflowTask, TransactionSubprocess, CallActivity
from SpiffWorkflow.dmn.specs import BusinessRuleTask

from SpiffWorkflow.spiff.parser.task_spec import SpiffTaskParser
from SpiffWorkflow.spiff.parser.task_spec import SubWorkflowParser, CallActivityParser
from SpiffWorkflow.spiff.parser.task_spec import BusinessRuleTaskParser

class SpiffBpmnParser(BpmnDmnParser):
    
    OVERRIDE_PARSER_CLASSES = {
        full_tag('task'): (SpiffTaskParser, NoneTask),
        full_tag('userTask'): (SpiffTaskParser, UserTask),
        full_tag('manualTask'): (SpiffTaskParser, ManualTask),
        full_tag('subProcess'): (SubWorkflowParser, SubWorkflowTask),
        full_tag('transaction'): (SubWorkflowParser, TransactionSubprocess),
        full_tag('callActivity'): (CallActivityParser, CallActivity),
        full_tag('businessRuleTask'): (BusinessRuleTaskParser, BusinessRuleTask)
    }