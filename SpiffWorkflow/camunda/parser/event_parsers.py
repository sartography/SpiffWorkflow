from SpiffWorkflow.bpmn.parser.event_parsers import EventDefinitionParser
from SpiffWorkflow.bpmn.parser.event_parsers import StartEventParser, EndEventParser, \
    IntermediateCatchEventParser, IntermediateThrowEventParser, BoundaryEventParser
from SpiffWorkflow.camunda.specs.events.event_definitions import MessageEventDefinition
from SpiffWorkflow.bpmn.parser.util import one


CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'


class CamundaEventDefinitionParser(EventDefinitionParser):

    def parse_message_event(self, message_event):
        """Parse a Camunda message event node."""

        message_ref = message_event.get('messageRef')
        if message_ref:
            message = one(self.doc_xpath('.//bpmn:message[@id="%s"]' % message_ref))
            name = message.get('name')
            correlations = self.get_message_correlations(message_ref)
        else:
            name = message_event.getparent().get('name')
            correlations = {}

        payload = message_event.attrib.get('{' + CAMUNDA_MODEL_NS + '}expression')
        result_var = message_event.attrib.get('{' + CAMUNDA_MODEL_NS + '}resultVariable')
        return MessageEventDefinition(name, correlations, payload, result_var)


# This really sucks, but it's still better than copy-pasting a bunch of code a million times
# The parser "design" makes it impossible to do anything sensible of intuitive here

class CamundaStartEventParser(CamundaEventDefinitionParser, StartEventParser):
    def create_task(self):
        return StartEventParser.create_task(self)

class CamundaEndEventParser(CamundaEventDefinitionParser, EndEventParser):
    def create_task(self):
        return EndEventParser.create_task(self)

class CamundaIntermediateCatchEventParser(CamundaEventDefinitionParser, IntermediateCatchEventParser):
    def create_task(self):
        return IntermediateCatchEventParser.create_task(self)

class CamundaIntermediateThrowEventParser(CamundaEventDefinitionParser, IntermediateThrowEventParser):
    def create_task(self):
        return IntermediateThrowEventParser.create_task(self)

class CamundaBoundaryEventParser(CamundaEventDefinitionParser, BoundaryEventParser):
    def create_task(self):
        return BoundaryEventParser.create_task(self)