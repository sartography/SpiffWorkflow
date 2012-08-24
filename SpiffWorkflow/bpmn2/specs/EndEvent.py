from SpiffWorkflow.bpmn2.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.Simple import Simple

__author__ = 'matth'

class EndEvent(Simple, BpmnSpecMixin):

    def _on_complete_hook(self, my_task):
        my_task.set_attribute(choice=self.description)
        super(EndEvent, self)._on_complete_hook(my_task)