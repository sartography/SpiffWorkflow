from SpiffWorkflow.bpmn.serializer.helpers.spec import EventDefinitionConverter

from SpiffWorkflow.spiff.specs.events.event_definitions import MessageEventDefinition

class MessageEventDefinitionConverter(EventDefinitionConverter):

    def __init__(self, registry):
        super().__init__(MessageEventDefinition, registry)

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['correlation_properties'] = self.correlation_properties_to_dict(event_definition.correlation_properties)
        dct['expression'] = event_definition.expression
        dct['message_var'] = event_definition.message_var
        return dct

    def from_dict(self, dct):
        dct['correlation_properties'] = self.correlation_properties_from_dict(dct['correlation_properties'])
        event_definition = super().from_dict(dct)
        return event_definition
