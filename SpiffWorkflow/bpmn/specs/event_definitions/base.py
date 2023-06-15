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

    def catch(self, my_task, event_definition=None):
        my_task._set_internal_data(event_fired=True)

    def throw(self, my_task):
        self._throw(my_task)

    def reset(self, my_task):
        my_task._set_internal_data(event_fired=False)

    def _throw(self, my_task, target=None, **kwargs):
        event_definition = kwargs.pop('event', my_task.task_spec.event_definition)
        my_task.workflow.top_workflow.catch(event_definition, target, **kwargs)

    def __eq__(self, other):
        return self.__class__ is other.__class__
