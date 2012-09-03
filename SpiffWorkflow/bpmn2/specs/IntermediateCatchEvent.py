from SpiffWorkflow.bpmn2.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.Simple import Simple

__author__ = 'matth'

class IntermediateCatchEvent(Simple, BpmnSpecMixin):

    def __init__(self, parent, name, event_spec, **kwargs):
        super(IntermediateCatchEvent, self).__init__(parent, name, **kwargs)
        self.event_spec = event_spec
