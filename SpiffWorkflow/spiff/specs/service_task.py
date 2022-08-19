from SpiffWorkflow.bpmn.specs.ServiceTask import ServiceTask
from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask

class ServiceTask(SpiffBpmnTask, ServiceTask):

    def __init__(self, wf_spec, name, operator_name, operator_params, **kwargs):

        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        self.operator_name = operator_name
        self.operator_params = operator_params

    def _execute(self, task):
        script = f'{self.operator_name}(**operator_params).execute()'
        task.workflow.servicetask_script_engine.execute(task, script, task.data, 
                external_methods={ 'operator_params': self.operator_params })
