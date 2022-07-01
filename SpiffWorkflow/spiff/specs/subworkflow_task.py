from ast import Pass
from SpiffWorkflow.bpmn.specs.SubWorkflowTask import SubWorkflowTask, TransactionSubprocess, CallActivity
from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask

class SubWorkflowTask(SpiffBpmnTask, SubWorkflowTask):

    def __init__(self, wf_spec, name, subworkflow_spec, transaction=False, **kwargs):

        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        # We don't so much as a class hierachy as a class pile and I'm giving up doing
        # this properly
        self.spec = subworkflow_spec
        self.transaction = transaction
        self.out_assign = []

class TransactionSubprocess(SpiffBpmnTask, TransactionSubprocess):

    def __init__(self, wf_spec, name, subworkflow_spec, transaction=True, **kwargs):

        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        self.spec = subworkflow_spec
        self.transaction = transaction
        self.out_assign = []

class CallActivity(SpiffBpmnTask, CallActivity):

    def __init__(self, wf_spec, name, subworkflow_spec, **kwargs):
        
        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        self.spec = subworkflow_spec
        self.out_assign = []
