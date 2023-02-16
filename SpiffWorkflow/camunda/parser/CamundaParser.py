
from SpiffWorkflow.bpmn.parser.BpmnParser import full_tag, DEFAULT_NSMAP

from SpiffWorkflow.bpmn.specs.ManualTask import ManualTask
from SpiffWorkflow.bpmn.specs.NoneTask import NoneTask
from SpiffWorkflow.bpmn.specs.ScriptTask import ScriptTask
from SpiffWorkflow.bpmn.specs.SubWorkflowTask import CallActivity, TransactionSubprocess

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.dmn.specs.BusinessRuleTask import BusinessRuleTask
from SpiffWorkflow.camunda.specs.UserTask import UserTask
from SpiffWorkflow.camunda.parser.task_spec import (
    CamundaTaskParser,
    BusinessRuleTaskParser,
    UserTaskParser,
    CallActivityParser,
    SubWorkflowParser,
    ScriptTaskParser,
)

from SpiffWorkflow.bpmn.specs.events.StartEvent import StartEvent
from SpiffWorkflow.bpmn.specs.events.EndEvent import EndEvent
from SpiffWorkflow.bpmn.specs.events.IntermediateEvent import IntermediateThrowEvent, IntermediateCatchEvent, BoundaryEvent
from .event_parsers import (
    CamundaStartEventParser,
    CamundaEndEventParser,
    CamundaIntermediateCatchEventParser,
    CamundaIntermediateThrowEventParser,
    CamundaBoundaryEventParser,
)

CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'
NSMAP = DEFAULT_NSMAP.copy()
NSMAP['camunda'] = CAMUNDA_MODEL_NS


class CamundaParser(BpmnDmnParser):

    OVERRIDE_PARSER_CLASSES = {
        full_tag('userTask'): (UserTaskParser, UserTask),
        full_tag('startEvent'): (CamundaStartEventParser, StartEvent),
        full_tag('endEvent'): (CamundaEndEventParser, EndEvent),
        full_tag('intermediateCatchEvent'): (CamundaIntermediateCatchEventParser, IntermediateCatchEvent),
        full_tag('intermediateThrowEvent'): (CamundaIntermediateThrowEventParser, IntermediateThrowEvent),
        full_tag('boundaryEvent'): (CamundaBoundaryEventParser, BoundaryEvent),
        full_tag('businessRuleTask'): (BusinessRuleTaskParser, BusinessRuleTask),
        full_tag('task'): (CamundaTaskParser, NoneTask),
        full_tag('manualTask'): (CamundaTaskParser, ManualTask),
        full_tag('scriptTask'): (ScriptTaskParser, ScriptTask),
        full_tag('subProcess'): (SubWorkflowParser, CallActivity),
        full_tag('callActivity'): (CallActivityParser, CallActivity),
        full_tag('transaction'): (SubWorkflowParser, TransactionSubprocess),
    }

    def __init__(self, namespaces=None, validator=None):
        super().__init__(namespaces=namespaces or NSMAP, validator=validator)