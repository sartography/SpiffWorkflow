from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.ExclusiveChoice import ExclusiveChoice

__author__ = 'matth'

class ExclusiveGateway(ExclusiveChoice, BpmnSpecMixin):
    pass