from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.Simple import Simple

__author__ = 'matth'

class StartEvent(Simple, BpmnSpecMixin):
    """
    Task Spec for a bpmn:startEvent node.
    """
    def __init__(self, parent, name, **kwargs):
        super(StartEvent, self).__init__(parent, name, **kwargs)