from .base import EventDefinition

class ItemAwareEventDefinition(EventDefinition):

    def __init__(self, name, description=None):
        super().__init__(name, description)


class ErrorEventDefinition(ItemAwareEventDefinition):
    """
    Error events can occur only in subprocesses and as subprocess boundary events.  They're
    matched by code rather than name.
    """

    def __init__(self, name, code=None, **kwargs):
        super(ErrorEventDefinition, self).__init__(name, **kwargs)
        self.code = code

    def __eq__(self, other):
        return super().__eq__(other) and self.code in [None, other.code]


class EscalationEventDefinition(ItemAwareEventDefinition):
    """
    Escalation events have names, though they don't seem to be used for anything.  Instead
    the spec says that the escalation code should be matched.
    """

    def __init__(self, name, code=None, **kwargs):
        """
        Constructor.

        :param escalation_code: The escalation code this event should
        react to. If None then all escalations will activate this event.
        """
        super(EscalationEventDefinition, self).__init__(name, **kwargs)
        self.code = code

    def __eq__(self, other):
        return super().__eq__(other) and self.code in [None, other.code]


class SignalEventDefinition(ItemAwareEventDefinition):
    """The SignalEventDefinition is the implementation of event definition used for Signal Events."""

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

    def __eq__(self, other):
        return super().__eq__(other) and self.name == other.name