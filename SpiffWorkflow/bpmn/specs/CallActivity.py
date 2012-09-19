from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.SubWorkflow import SubWorkflow
from SpiffWorkflow.specs.TaskSpec import TaskSpec

__author__ = 'matth'

class CallActivity(SubWorkflow, BpmnSpecMixin):

    def __init__(self, parent, name, wf_spec=None, wf_class=None, **kwargs):
        super(CallActivity, self).__init__(parent, name, None, **kwargs)
        self.spec = wf_spec
        self.wf_class = wf_class

    def test(self):
        TaskSpec.test(self)

    def _create_subworkflow(self, my_task):
        return self.get_workflow_class()(self.spec, name=self.name,
            read_only = my_task.workflow.read_only,
            script_engine=my_task.workflow.outer_workflow.script_engine,
            parent = my_task.workflow.outer_workflow)

    def get_workflow_class(self):
        return self.wf_class

    def _on_subworkflow_completed(self, subworkflow, my_task):
        super(CallActivity,self)._on_subworkflow_completed(subworkflow, my_task)
        if isinstance(my_task.parent.task_spec, BpmnSpecMixin):
            my_task.parent.task_spec._child_complete_hook(my_task)
