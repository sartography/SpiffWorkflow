from ..specs.UserTask import UserTask
from ..parser.UserTaskParser import UserTaskParser
from ...bpmn.parser.BpmnParser import BpmnParser, full_tag

from SpiffWorkflow.bpmn.specs.events import EndEvent, IntermediateThrowEvent
from ..specs.events.event_types import StartEvent, IntermediateCatchEvent, BoundaryEvent
from .event_parsers import CamundaStartEventParser, CamundaEndEventParser, \
    CamundaIntermediateCatchEventParser, CamundaIntermediateThrowEventParser, CamundaBoundaryEventParser


class CamundaParser(BpmnParser):
    OVERRIDE_PARSER_CLASSES = {
        full_tag('userTask'): (UserTaskParser, UserTask),
        full_tag('startEvent'): (CamundaStartEventParser, StartEvent),
        full_tag('endEvent'): (CamundaEndEventParser, EndEvent),
        full_tag('intermediateCatchEvent'): (CamundaIntermediateCatchEventParser, IntermediateCatchEvent),
        full_tag('intermediateThrowEvent'): (CamundaIntermediateThrowEventParser, IntermediateThrowEvent),
        full_tag('boundaryEvent'): (CamundaBoundaryEventParser, BoundaryEvent),
    }
