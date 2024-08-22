from copy import deepcopy

from SpiffWorkflow.bpmn.util import BpmnEvent, PendingBpmnEvent
from .base import EventDefinition

class ItemAwareEventDefinition(EventDefinition):

    def __init__(self, name, description=None):
        super().__init__(name, description)

    def catch(self, my_task, event=None):
        my_task.internal_data[self.name] = event.payload
        super().catch(my_task, event)

    def throw(self, my_task):
        payload = deepcopy(my_task.data)
        event = BpmnEvent(self, payload=payload)
        my_task.workflow.top_workflow.catch(event)

    def update_task_data(self, my_task):
        payload = my_task.internal_data.get(self.name)
        if payload is not None:
            my_task.set_data(**payload)

    def reset(self, my_task):
        my_task.internal_data.pop(self.name, None)
        super().reset(my_task)


class CodeEventDefinition(ItemAwareEventDefinition):

    def __init__(self, name, code=None, **kwargs):
        super().__init__(name, **kwargs)
        self.code = code

    def throw(self, my_task):
        payload = deepcopy(my_task.data)
        event = BpmnEvent(self, payload=payload, target=my_task.workflow)
        my_task.workflow.top_workflow.catch(event)

    def details(self, my_task):
        return PendingBpmnEvent(self.name, self.__class__.__name__, self.code)

    def __eq__(self, other):
        return super().__eq__(other) and self.code in [None, other.code]


class ErrorEventDefinition(CodeEventDefinition):
    """
    Error events can occur only in subprocesses and as subprocess boundary events.  They're
    matched by code rather than name.
    """
    pass

class EscalationEventDefinition(CodeEventDefinition):
    """
    Escalation events have names, though they don't seem to be used for anything.  Instead
    the spec says that the escalation code should be matched.
    """
    pass


class SignalEventDefinition(ItemAwareEventDefinition):
    """The SignalEventDefinition is the implementation of event definition used for Signal Events."""

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

    def __eq__(self, other):
        return super().__eq__(other) and self.name == other.name
