from SpiffWorkflow.bpmn.event import BpmnEvent

from .base import EventDefinition

class NoneEventDefinition(EventDefinition):
    """This class defines behavior for NoneEvents.  We override throw to do nothing."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def throw(self, my_task):
        """It's a 'none' event, so nothing to throw."""
        pass

    def reset(self, my_task):
        """It's a 'none' event, so nothing to reset."""
        pass


class CancelEventDefinition(EventDefinition):
    """Cancel events are only handled by the outerworkflow, as they can only be used inside of transaction subprocesses."""

    def __init__(self, **kwargs):
        super(CancelEventDefinition, self).__init__(**kwargs)

    def throw(self, my_task, **kwargs):
        event = BpmnEvent(self, target=my_task.workflow.parent_workflow)
        my_task.workflow.top_workflow.catch(event)


class TerminateEventDefinition(EventDefinition):
    """The TerminateEventDefinition is the implementation of event definition used for Termination Events."""

    def __init__(self, **kwargs):
        super(TerminateEventDefinition, self).__init__(**kwargs)

    def throw(self, my_task):
        event = BpmnEvent(my_task.task_spec.event_definition, target=my_task.workflow)
        my_task.workflow.top_workflow.catch(event)