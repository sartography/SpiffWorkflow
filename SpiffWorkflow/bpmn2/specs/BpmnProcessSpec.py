from SpiffWorkflow.bpmn2.specs.ParallelGateway import ParallelGateway
from SpiffWorkflow.specs.Join import Join
from SpiffWorkflow.specs.Simple import Simple
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec

__author__ = 'matth'

class EndJoin(ParallelGateway):
    pass

class BpmnProcessSpec(WorkflowSpec):

    def __init__(self, name=None, filename=None):
        super(BpmnProcessSpec, self).__init__(name=name, filename=filename)
        self.end = EndJoin(self, '%s.EndJoin' % (self.name))
        end = Simple(self, 'End')
        end.follow(self.end)
        self._is_single_threaded = None

    def is_single_threaded(self):
        return self._is_single_threaded

