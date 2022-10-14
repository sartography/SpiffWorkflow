from SpiffWorkflow.bpmn.specs.SubWorkflowTask import SubWorkflowTask, TransactionSubprocess, CallActivity
from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask

class SubWorkflowTask(SubWorkflowTask, SpiffBpmnTask):

    def __init__(self, wf_spec, name, subworkflow_spec, transaction=False, **kwargs):

        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        # We don't so much as a class hierachy as a class pile and I'm giving up doing
        # this properly
        self.spec = subworkflow_spec
        self.transaction = transaction
        self.in_assign = []
        self.out_assign = []

    def _on_ready_hook(self, my_task):
        SpiffBpmnTask._on_ready_hook(self, my_task)
        self.start_workflow(my_task)

    def _on_complete_hook(self, my_task):
        SpiffBpmnTask._on_complete_hook(self, my_task)

    @property
    def spec_type(self):
        return 'Subprocess'


class TransactionSubprocess(SubWorkflowTask, TransactionSubprocess):

    def __init__(self, wf_spec, name, subworkflow_spec, transaction=True, **kwargs):

        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        self.spec = subworkflow_spec
        self.transaction = transaction
        self.in_assign = []
        self.out_assign = []

    @property
    def spec_type(self):
        return 'Transactional Subprocess'


class CallActivity(SubWorkflowTask, CallActivity):

    def __init__(self, wf_spec, name, subworkflow_spec, **kwargs):
        
        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        self.spec = subworkflow_spec
        self.in_assign = []
        self.out_assign = []

    @property
    def spec_type(self):
        return 'Call Activity'
