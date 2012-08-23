__author__ = 'matth'

class BpmnSpecMixin(object):

    def _init(self):
        if not hasattr(self, 'outgoing_names'):
            self.outgoing_names = {}

    def connect_outgoing(self, taskspec, sequence_flow_name):
        self._init()
        if taskspec not in self.outputs:
            self.connect(taskspec)
        self.outgoing_names[sequence_flow_name] = taskspec

    def connect_outgoing_if(self, condition, taskspec, sequence_flow_name):
        self._init()
        if taskspec not in self.outputs:
            self.connect_if(condition, taskspec)
        self.outgoing_names[sequence_flow_name] = taskspec

    def get_outgoing_sequence_names(self):
        self._init()
        return self.outgoing_names.keys()


