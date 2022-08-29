from SpiffWorkflow.bpmn.parser.event_parsers import EventDefinitionParser, ReceiveTaskParser
from SpiffWorkflow.bpmn.parser.event_parsers import StartEventParser, EndEventParser, \
    IntermediateCatchEventParser, IntermediateThrowEventParser, BoundaryEventParser, \
    SendTaskParser
from SpiffWorkflow.spiff.specs.events.event_definitions import MessageEventDefinition
from SpiffWorkflow.bpmn.parser.util import one
from SpiffWorkflow.spiff.parser.task_spec import SpiffTaskParser


class SpiffEventDefinitionParser(SpiffTaskParser, EventDefinitionParser):

    def parse_message_event(self, message_event):
        """Parse a Spiff message event."""

        message_ref = message_event.get('messageRef')
        if message_ref:
            message = one(self.doc_xpath('.//bpmn:message[@id="%s"]' % message_ref))
            name = message.get('name')
            extensions = self.parse_extensions(message)
            correlations = self.get_message_correlations(message_ref)
        else:
            name = message_event.getparent().get('name')
            extensions = {}
            correlations = []

        return MessageEventDefinition(name, correlations, 
            expression=extensions.get('messagePayload'),
            message_var=extensions.get('messageVariable')
        )


class SpiffStartEventParser(SpiffEventDefinitionParser, StartEventParser):
    def create_task(self):
        return StartEventParser.create_task(self)

class SpiffEndEventParser(SpiffEventDefinitionParser, EndEventParser):
    def create_task(self):
        return EndEventParser.create_task(self)

class SpiffIntermediateCatchEventParser(SpiffEventDefinitionParser, IntermediateCatchEventParser):
    def create_task(self):
        return IntermediateCatchEventParser.create_task(self)

class SpiffIntermediateThrowEventParser(SpiffEventDefinitionParser, IntermediateThrowEventParser):
    def create_task(self):
        return IntermediateThrowEventParser.create_task(self)

class SpiffBoundaryEventParser(SpiffEventDefinitionParser, BoundaryEventParser):
    def create_task(self):
        return BoundaryEventParser.create_task(self)

class SpiffSendTaskParser(SpiffEventDefinitionParser, SendTaskParser):
    def create_task(self):
        return SendTaskParser.create_task(self)

class SpiffReceiveTaskParser(SpiffEventDefinitionParser, ReceiveTaskParser):
    def create_task(self):
        return ReceiveTaskParser.create_task(self)