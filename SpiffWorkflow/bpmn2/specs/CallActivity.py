from SpiffWorkflow.bpmn2.BpmnWorkflow import BpmnWorkflow
from SpiffWorkflow.bpmn2.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.operators import Assign
from SpiffWorkflow.specs.SubWorkflow import SubWorkflow
from SpiffWorkflow.specs.TaskSpec import TaskSpec

__author__ = 'matth'

class CallActivity(SubWorkflow, BpmnSpecMixin):

    def __init__(self, parent, name, wf_spec, **kwargs):
        super(CallActivity, self).__init__(parent, name, None, out_assign=[Assign('choice', 'choice')], **kwargs)
        self.spec = wf_spec

    def test(self):
        TaskSpec.test(self)

    def _create_workflow_spec(self, my_task):
        return BpmnWorkflow(self.spec, name=self.name, parent = my_task.workflow.outer_workflow)

