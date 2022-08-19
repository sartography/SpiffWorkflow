from SpiffWorkflow.bpmn.specs.ServiceTask import ServiceTask
from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask

class ServiceTask(SpiffBpmnTask, ServiceTask):

    def __init__(self, wf_spec, name, operator_name, operator_params, **kwargs):

        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        self.operator_name = operator_name
        self.operator_param = operator_params

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
