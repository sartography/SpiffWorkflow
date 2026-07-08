from SpiffWorkflow.bpmn.util.event import BpmnEvent
from .timer import TimerEventDefinition, EventDefinition

class MultipleEventDefinition(EventDefinition):

    def __init__(self, event_definitions=None, parallel=False, **kwargs):
        super().__init__(**kwargs)
        self.event_definitions = event_definitions or []
        self.parallel = parallel

    def has_fired(self, my_task):

        event_definitions = list(self.event_definitions)
        seen_events = my_task.internal_data.get('seen_events', [])
        for event in seen_events:
            if event.event_definition in event_definitions:
                event_definitions.remove(event.event_definition)

        for event_definition in event_definitions:
            if isinstance(event_definition, TimerEventDefinition):
                if event_definition.has_fired(my_task):
                    event_definitions.remove(event_definition)
                    seen_events.append(BpmnEvent(event_definition))

        my_task.internal_data['seen_events'] = seen_events

        if self.parallel:
            # Parallel multiple need to match all events
            return len(event_definitions) == 0
        else:
            return len(seen_events) > 0

    def catches(self, my_task, event=None):
        for item in self.event_definitions:
            if item.catches(my_task, event):
                return True

    def catch(self, my_task, event=None):
        for item in self.event_definitions:
            if item.catches(my_task, event):
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
