from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.parser.BpmnParser import full_tag

from SpiffWorkflow.spiff.specs import NoneTask, ManualTask, UserTask, SubWorkflowTask, TransactionSubprocess, CallActivity
from SpiffWorkflow.spiff.parser.task import SpiffTaskParser, SubWorkflowParser, CallActivityParser

class SpiffBpmnParser(BpmnParser):
    OVERRIDE_PARSER_CLASSES = {
        full_tag('task'): (SpiffTaskParser, NoneTask),
        full_tag('userTask'): (SpiffTaskParser, UserTask),
        full_tag('manualTask'): (SpiffTaskParser, ManualTask),
        full_tag('subProcess'): (SubWorkflowParser, SubWorkflowTask),
        full_tag('transaction'): (SubWorkflowParser, TransactionSubprocess),
        full_tag('callActivity'): (CallActivityParser, CallActivity),
    }