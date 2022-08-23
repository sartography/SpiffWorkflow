from SpiffWorkflow.bpmn.specs.ServiceTask import ServiceTask
from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask

class ServiceTask(SpiffBpmnTask, ServiceTask):

    def __init__(self, wf_spec, name, operation_name, operation_params, **kwargs):
        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        self.operation_name = operation_name
        self.operation_params = operation_params

    def _execute(self, task):
        def evaluate(expression):
            return task.workflow.servicetask_script_engine.evaluate(task, repr(expression))

        operation_params_var_name = 'spiff__operation_params'
        evaluated_params = {k: evaluate(v) for k, v in self.operation_params.items()}
        script = f'{self.operation_name}(**{operation_params_var_name}).execute()'

        task.workflow.servicetask_script_engine.execute(task, script, task.data, 
                external_methods={ operation_params_var_name: evaluated_params })
