from SpiffWorkflow.bpmn.specs.events.event_types import CatchingEvent
from SpiffWorkflow.bpmn.specs.events import StartEvent
from .event_definitions import MessageEventDefinition

class CatchingEvent(CatchingEvent):

    def _on_complete_hook(self, my_task):
        if isinstance(self.event_definition, MessageEventDefinition):
            # If we are a message event, then we need to copy the event data out of
            # our internal data and into the task data
            event_data = my_task.internal_data[self.event_definition.name]
            my_task.data[event_data['result_var']] = event_data['payload']
        super(CatchingEvent, self)._on_complete_hook(my_task)


class StartEvent(CatchingEvent, StartEvent):
    pass

class IntermediateCatchEvent(CatchingEvent):
    pass

class BoundaryEvent(CatchingEvent):

    def __init__(self, wf_spec, name, event_definition, cancel_activity, **kwargs):
        super(BoundaryEvent, self).__init__(wf_spec, name, event_definition, **kwargs)
        self.cancel_activity = cancel_activity