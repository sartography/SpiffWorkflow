from copy import deepcopy

from SpiffWorkflow.exceptions import WorkflowException
from .base import EventDefinition

class CorrelationProperty:
    """Rules for generating a correlation key when a message is sent or received."""

    def __init__(self, name, retrieval_expression, correlation_keys):
        self.name = name                                    # This is the property name
        self.retrieval_expression = retrieval_expression    # This is how it's generated
        self.correlation_keys = correlation_keys            # These are the keys it's used by


class MessageEventDefinition(EventDefinition):
    """The default message event."""

    def __init__(self, name, correlation_properties=None, **kwargs):
        super().__init__(name, **kwargs)
        self.correlation_properties = correlation_properties or []
        self.payload = None

    def catch(self, my_task, event_definition=None):
        self.update_internal_data(my_task, event_definition)
        super(MessageEventDefinition, self).catch(my_task, event_definition)

    def throw(self, my_task):
        # We can't update our own payload, because if this task is reached again
        # we have to evaluate it again so we have to create a new event
        event = MessageEventDefinition(self.name, self.correlation_properties)
        # Generating a payload unfortunately needs to be handled using custom extensions
        # However, there needs to be something to apply the correlations to in the
        # standard case and this is line with the way Spiff works otherwise
        event.payload = deepcopy(my_task.data)
        correlations = self.get_correlations(my_task, event.payload)
        my_task.workflow.correlations.update(correlations)
        self._throw(my_task, event=event, correlations=correlations)

    def update_internal_data(self, my_task, event_definition):
        my_task.internal_data[event_definition.name] = event_definition.payload

    def update_task_data(self, my_task):
        # I've added this method so that different message implementations can handle
        # copying their message data into the task
        payload = my_task.internal_data.get(self.name)
        if payload is not None:
            my_task.set_data(**payload)

    def get_correlations(self, task, payload):
        correlations = {}
        for property in self.correlation_properties:
            for key in property.correlation_keys:
                if key not in correlations:
                    correlations[key] = {}
                try:
                    correlations[key][property.name] = task.workflow.script_engine._evaluate(property.retrieval_expression, payload)
                except WorkflowException:
                    # Just ignore missing keys.  The dictionaries have to match exactly
                    pass
        return correlations

    def __eq__(self, other):
        return super().__eq__(other) and self.name == other.name