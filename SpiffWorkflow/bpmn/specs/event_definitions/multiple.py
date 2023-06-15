from SpiffWorkflow.bpmn.event import BpmnEvent
from .timer import TimerEventDefinition, EventDefinition

class MultipleEventDefinition(EventDefinition):

    def __init__(self, event_definitions=None, parallel=False, **kwargs):
        super().__init__(**kwargs)
        self.event_definitions = event_definitions or []
        self.parallel = parallel

    def has_fired(self, my_task):

        event_definitions = list(self.event_definitions)
        seen_events = my_task.internal_data.get('seen_events', [])
        for event_definition in self.event_definitions:
            if isinstance(event_definition, TimerEventDefinition):
                child = [c for c in my_task.children if c.task_spec.event_definition == event_definition]
                child[0].task_spec._update_hook(child[0])
                if event_definition.has_fired(child[0]) and event_definition in event_definitions:
                    event_definitions.remove(event_definition)
            else:
                for event in seen_events:
                    if event_definition.catches(my_task, event) and event_definition in event_definitions:
                        event_definitions.remove(event_definition)

        if self.parallel:
            # Parallel multiple need to match all events
            return len(event_definitions) == 0
        else:
            return len(seen_events) > 0

    def catch(self, my_task, event=None):
        event.event_definition.catch(my_task, event)
        seen_events = my_task.internal_data.get('seen_events', []) + [event]
        my_task._set_internal_data(seen_events=seen_events)

    def reset(self, my_task):
        my_task.internal_data.pop('seen_events', None)
        super().reset(my_task)

    def __eq__(self, other):
        # This event can catch any of the events associated with it
        for event in self.event_definitions:
            if event == other:
                return True
        return False

    def throw(self, my_task):
        # Mutiple events throw all associated events when they fire
        for event_definition in self.event_definitions:
            event_definition.throw(my_task)