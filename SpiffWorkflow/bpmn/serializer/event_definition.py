from .helpers.spec import EventDefinitionConverter

from ..specs.events.event_definitions import (
    CancelEventDefinition,
    ErrorEventDefinition,
    EscalationEventDefinition,
    MessageEventDefinition,
    NoneEventDefinition,
    SignalEventDefinition,
    TerminateEventDefinition,
    TimeDateEventDefinition,
    DurationTimerEventDefinition,
    CycleTimerEventDefinition,
    MultipleEventDefinition,
)

class CancelEventDefinitionConverter(EventDefinitionConverter):
    def __init__(self, registry):
        super().__init__(CancelEventDefinition, registry)


class ErrorEventDefinitionConverter(EventDefinitionConverter):

    def __init__(self, registry):
        super().__init__(ErrorEventDefinition, registry)

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['error_code'] = event_definition.error_code
        return dct


class EscalationEventDefinitionConverter(EventDefinitionConverter):

    def __init__(self, registry):
        super().__init__(EscalationEventDefinition, registry)

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['escalation_code'] = event_definition.escalation_code
        return dct


class MessageEventDefinitionConverter(EventDefinitionConverter):

    def __init__(self, registry):
        super().__init__(MessageEventDefinition, registry)

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['correlation_properties'] = self.correlation_properties_to_dict(event_definition.correlation_properties)
        return dct

    def from_dict(self, dct):
        dct['correlation_properties'] = self.correlation_properties_from_dict(dct['correlation_properties'])
        event_definition = super().from_dict(dct)
        return event_definition


class NoneEventDefinitionConverter(EventDefinitionConverter):
    def __init__(self, registry):
        super().__init__(NoneEventDefinition, registry)


class SignalEventDefinitionConverter(EventDefinitionConverter):
    def __init__(self, registry):
        super().__init__(SignalEventDefinition, registry)


class TerminateEventDefinitionConverter(EventDefinitionConverter):
    def __init__(self, registry):
        super().__init__(TerminateEventDefinition, registry)


class TimerEventDefinitionConverter(EventDefinitionConverter):

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['expression'] = event_definition.expression
        return dct

class TimeDateEventDefinitionConverter(TimerEventDefinitionConverter):
    def __init__(self, registry):
        super().__init__(TimeDateEventDefinition, registry)


class DurationTimerEventDefinitionConverter(TimerEventDefinitionConverter):
    def __init__(self, registry):
        super().__init__(DurationTimerEventDefinition, registry)


class CycleTimerEventDefinitionConverter(TimerEventDefinitionConverter):
    def __init__(self, registry):
        super().__init__(CycleTimerEventDefinition, registry)


class MultipleEventDefinitionConverter(EventDefinitionConverter):

    def __init__(self, registry):
        super().__init__(MultipleEventDefinition, registry)

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['parallel'] = event_definition.parallel
        dct['event_definitions'] = [self.registry.convert(e) for e in event_definition.event_definitions]
        return dct

    def from_dict(self, dct):
        events = dct.pop('event_definitions')
        event_definition = super().from_dict(dct)
        event_definition.event_definitions = [self.registry.restore(d) for d in events]
        return event_definition


DEFAULT_EVENT_CONVERTERS = [
    CancelEventDefinitionConverter,
    ErrorEventDefinitionConverter,
    EscalationEventDefinitionConverter,
    MessageEventDefinitionConverter,
    NoneEventDefinitionConverter,
    SignalEventDefinitionConverter,
    TerminateEventDefinitionConverter,
    TimeDateEventDefinitionConverter,
    DurationTimerEventDefinitionConverter,
    CycleTimerEventDefinitionConverter,
    MultipleEventDefinitionConverter,
]