from SpiffWorkflow.specs.TaskSpec import TaskSpec

__author__ = 'matth'

class BpmnSpecMixin(TaskSpec):


    def __init__(self, parent, name, lane=None, **kwargs):
        super(BpmnSpecMixin, self).__init__(parent, name, **kwargs)
        self.outgoing_names = {}
        self.lane = lane

    def connect_outgoing(self, taskspec, sequence_flow_name):
        if taskspec not in self.outputs:
            self.connect(taskspec)
        self.outgoing_names[sequence_flow_name] = taskspec

    def connect_outgoing_if(self, condition, taskspec, sequence_flow_name):
        if taskspec not in self.outputs:
            self.connect_if(condition, taskspec)
        self.outgoing_names[sequence_flow_name] = taskspec

    def get_outgoing_sequence_names(self):
        return self.outgoing_names.keys()

    def accept_message(self, my_task, message):
        return False

