from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.bpmn.parser.BpmnParser import full_tag

from SpiffWorkflow.bpmn.specs.events import StartEvent, EndEvent, IntermediateThrowEvent, BoundaryEvent, IntermediateCatchEvent
from SpiffWorkflow.spiff.specs import NoneTask, ManualTask, UserTask, ScriptTask, SubWorkflowTask, TransactionSubprocess, CallActivity, ServiceTask
from SpiffWorkflow.spiff.specs.events.event_types import SendTask, ReceiveTask
from SpiffWorkflow.spiff.parser.task_spec import SpiffTaskParser, SubWorkflowParser, CallActivityParser, ServiceTaskParser, ScriptTaskParser
from SpiffWorkflow.spiff.parser.event_parsers import (SpiffStartEventParser, SpiffEndEventParser, SpiffBoundaryEventParser,
    SpiffIntermediateCatchEventParser, SpiffIntermediateThrowEventParser, SpiffSendTaskParser, SpiffReceiveTaskParser)
from SpiffWorkflow.dmn.specs import BusinessRuleTask

from SpiffWorkflow.spiff.parser.task_spec import BusinessRuleTaskParser

class SpiffBpmnParser(BpmnDmnParser):

    OVERRIDE_PARSER_CLASSES = {
        full_tag('task'): (SpiffTaskParser, NoneTask),
        full_tag('userTask'): (SpiffTaskParser, UserTask),
        full_tag('manualTask'): (SpiffTaskParser, ManualTask),
        full_tag('scriptTask'): (ScriptTaskParser, ScriptTask),
        full_tag('subProcess'): (SubWorkflowParser, SubWorkflowTask),
        full_tag('transaction'): (SubWorkflowParser, TransactionSubprocess),
        full_tag('callActivity'): (CallActivityParser, CallActivity),
        full_tag('serviceTask'): (ServiceTaskParser, ServiceTask),
        full_tag('startEvent'): (SpiffStartEventParser, StartEvent),
        full_tag('endEvent'): (SpiffEndEventParser, EndEvent),
        full_tag('boundaryEvent'): (SpiffBoundaryEventParser, BoundaryEvent),
        full_tag('intermediateCatchEvent'): (SpiffIntermediateCatchEventParser, IntermediateCatchEvent),
        full_tag('intermediateThrowEvent'): (SpiffIntermediateThrowEventParser, IntermediateThrowEvent),
        full_tag('sendTask'): (SpiffSendTaskParser, SendTask),
        full_tag('receiveTask'): (SpiffReceiveTaskParser, ReceiveTask),
        full_tag('businessRuleTask'): (BusinessRuleTaskParser, BusinessRuleTask)
    }
