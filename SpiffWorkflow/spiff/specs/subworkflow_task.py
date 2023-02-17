from SpiffWorkflow.bpmn.specs.SubWorkflowTask import (
    SubWorkflowTask as DefaultSubWorkflow,
    TransactionSubprocess as DefaultTransaction,
    CallActivity as DefaultCallActivity,
)
from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask


class SubWorkflowTask(DefaultSubWorkflow, SpiffBpmnTask):

    def __init__(self, wf_spec, name, subworkflow_spec, transaction=False, **kwargs):

        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        # We don't so much as a class hierachy as a class pile and I'm giving up doing
        # this properly
        self.spec = subworkflow_spec
        self.transaction = transaction
        self.in_assign = []
        self.out_assign = []

    def _update_hook(self, my_task):
        # Don't really like duplicating this, but we need to run SpiffBpmn update rather than the default
        wf = my_task.workflow._get_outermost_workflow(my_task)
        if my_task.id not in wf.subprocesses:
            SpiffBpmnTask._update_hook(self, my_task)
            self.create_workflow(my_task)
            return True

    def _on_complete_hook(self, my_task):
        SpiffBpmnTask._on_complete_hook(self, my_task)

    @property
    def spec_type(self):
        return 'Subprocess'


class TransactionSubprocess(SubWorkflowTask, DefaultTransaction):

    def __init__(self, wf_spec, name, subworkflow_spec, transaction=True, **kwargs):

        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        self.spec = subworkflow_spec
        self.transaction = transaction
        self.in_assign = []
        self.out_assign = []

    @property
    def spec_type(self):
        return 'Transactional Subprocess'


class CallActivity(SubWorkflowTask, DefaultCallActivity):

    def __init__(self, wf_spec, name, subworkflow_spec, **kwargs):
        
        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        self.spec = subworkflow_spec
        self.in_assign = []
        self.out_assign = []

    @property
    def spec_type(self):
        return 'Call Activity'
