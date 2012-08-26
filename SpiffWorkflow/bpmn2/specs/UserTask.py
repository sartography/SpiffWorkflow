from SpiffWorkflow.bpmn2.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.bpmn2.specs.ExclusiveGateway import ExclusiveGateway
from SpiffWorkflow.specs.Simple import Simple

__author__ = 'matth'

class UserTask(Simple, BpmnSpecMixin):

    def get_user_choices(self):
        if not self.outputs:
            return []
        assert len(self.outputs) == 1
        next_node = self.outputs[0]
        if isinstance(next_node, ExclusiveGateway):
            return next_node.get_outgoing_sequence_names()
        return self.get_outgoing_sequence_names()

    def do_choice(self, task, choice):
        task.set_attribute(choice=choice)
        task.complete()