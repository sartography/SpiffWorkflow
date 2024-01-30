from SpiffWorkflow.bpmn.util import BpmnEvent, PendingBpmnEvent

class EventDefinition(object):
    """
    This is the base class for Event Definitions.  It implements the default throw/catch
    behavior for events.

    If internal is true, this event should be thrown to the current workflow
    If external is true, this event should be thrown to the outer workflow

    Default throw behavior is to send the event based on the values of the internal
    and external flags.
    Default catch behavior is to set the event to fired
    """
    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description

    def has_fired(self, my_task):
        return my_task._get_internal_data('event_fired', False)

    def catches(self, my_task, event):
        return self == event.event_definition

    def catch(self, my_task, event=None):
        my_task._set_internal_data(event_fired=True)

    def throw(self, my_task):
        event = BpmnEvent(self)
        my_task.workflow.top_workflow.catch(event)

    def update_task_data(self, my_task):
        """This method allows events with payloads mrege them into the task"""
        pass

    def reset(self, my_task):
        my_task._set_internal_data(event_fired=False)

    def details(self, my_task):
        return PendingBpmnEvent(self.name, self.__class__.__name__)

    def __eq__(self, other):
        return self.__class__ is other.__class__
