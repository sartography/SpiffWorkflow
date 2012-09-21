from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.Simple import Simple

__author__ = 'matth'

class UserTask(Simple, BpmnSpecMixin):
    """
    Task Spec for a bpmn:userTask node.
    """
    def is_engine_task(self):
        return False
