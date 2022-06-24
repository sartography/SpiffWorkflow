from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from SpiffWorkflow.bpmn.parser.util import xpath_eval

class SignavioBpmnParser(BpmnParser):

    def add_bpmn_xml(self, bpmn, filename=None):
        # signavio sometimes disconnects a BoundaryEvent from it's owning task
        # They then show up as intermediateCatchEvents without any incoming
        # sequence flows.  Check for this case before parsing the XML.
        xpath = xpath_eval(bpmn)
        for catch_event in xpath('.//bpmn:intermediateCatchEvent'):
            incoming = xpath('.//bpmn:sequenceFlow[@targetRef="%s"]' % catch_event.get('id'))
            if not incoming:
                raise ValidationException(
                    'Intermediate Catch Event has no incoming sequences. '
                    'This might be a Boundary Event that has been '
                    'disconnected.',
                    node=catch_event, filename=filename)
        return super().add_bpmn_xml(bpmn, filename)