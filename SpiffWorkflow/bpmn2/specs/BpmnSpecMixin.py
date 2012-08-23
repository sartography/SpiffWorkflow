__author__ = 'matth'

class BpmnSpecMixin(object):

    def _init(self):
        if not hasattr(self, 'outgoing_names'):
            self.outgoing_names = {}

    def connect_outgoing(self, taskspec, sequence_flow_name):
        self._init()
        self.connect(taskspec)
        self.outgoing_names[taskspec.name] = sequence_flow_name

    def connect_outgoing_if(self, condition, taskspec, sequence_flow_name):
        self._init()
        self.connect_if(condition, taskspec)
        self.outgoing_names[taskspec.name] = sequence_flow_name

    def get_sequence_flow_name(self, taskspec):
        self._init()
        return self.outgoing_names[taskspec.name]

    def get_outgoing_sequence_names(self):
        return self.outgoing_names.values()


