from SpiffWorkflow.bpmn2.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.Simple import Simple

__author__ = 'matth'

class StartEvent(Simple, BpmnSpecMixin):

    def __init__(self, parent, name, **kwargs):
        super(StartEvent, self).__init__(parent, name, **kwargs)