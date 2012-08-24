from SpiffWorkflow.bpmn2.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.Simple import Simple

__author__ = 'matth'

class EndEvent(Simple, BpmnSpecMixin):

    def __init__(self, parent, name, is_terminate_event=False, **kwargs):
        super(EndEvent, self).__init__(parent, name, **kwargs)
        self.is_terminate_event = is_terminate_event

    def _on_complete_hook(self, my_task):
        if self.is_terminate_event:
            my_task.workflow.ready_to_end(my_task)

        my_task.set_attribute(choice=self.description)
        super(EndEvent, self)._on_complete_hook(my_task)