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

from ..specs.events.event_definitions import CorrelationProperty

class CancelEventDefinitionConverter(EventDefinitionConverter):
    def __init__(self, registry, typename=None):
        super().__init__(CancelEventDefinition, registry, typename)


class ErrorEventDefinitionConverter(EventDefinitionConverter):

    def __init__(self, registry, typename=None):
        super().__init__(ErrorEventDefinition, registry, typename)

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['error_code'] = event_definition.error_code
        return dct


class EscalationEventDefinitionConverter(EventDefinitionConverter):

    def __init__(self, registry, typename=None):
        super().__init__(EscalationEventDefinition, registry, typename)

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['escalation_code'] = event_definition.escalation_code
        return dct


class MessageEventDefinitionConverter(EventDefinitionConverter):

    def __init__(self, registry, typename=None):
        super().__init__(MessageEventDefinition, registry, typename)

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['correlation_properties'] = [prop.__dict__ for prop in event_definition.correlation_properties]
        return dct

    def from_dict(self, dct):
        dct['correlation_properties'] = [CorrelationProperty(**prop) for prop in dct['correlation_properties']]
        event_definition = super().from_dict(dct)
        return event_definition


class NoneEventDefinitionConverter(EventDefinitionConverter):
    def __init__(self, registry, typename=None):
        super().__init__(NoneEventDefinition, registry, typename)


class SignalEventDefinitionConverter(EventDefinitionConverter):
    def __init__(self, registry, typename=None):
        super().__init__(SignalEventDefinition, registry, typename)


class TerminateEventDefinitionConverter(EventDefinitionConverter):
    def __init__(self, registry, typename=None):
        super().__init__(TerminateEventDefinition, registry, typename)


class TimerEventDefinitionConverter(EventDefinitionConverter):

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['expression'] = event_definition.expression
        return dct

class TimeDateEventDefinitionConverter(TimerEventDefinitionConverter):
    def __init__(self, registry, typename=None):
        super().__init__(TimeDateEventDefinition, registry, typename)


class DurationTimerEventDefinitionConverter(TimerEventDefinitionConverter):
    def __init__(self, registry, typename=None):
        super().__init__(DurationTimerEventDefinition, registry, typename)


class CycleTimerEventDefinitionConverter(TimerEventDefinitionConverter):
    def __init__(self, registry, typename=None):
        super().__init__(CycleTimerEventDefinition, registry, typename)


class MultipleEventDefinitionConverter(EventDefinitionConverter):

    def __init__(self, registry, typename=None):
        super().__init__(MultipleEventDefinition, registry, typename)

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