import json
from SpiffWorkflow.bpmn.specs.ServiceTask import ServiceTask
from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask

class ServiceTask(SpiffBpmnTask, ServiceTask):

    def __init__(self, wf_spec, name, operation_name, operation_params, result_variable, **kwargs):
        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        self.operation_name = operation_name
        self.operation_params = operation_params
        self.result_variable = result_variable

    def _result_variable(self, task):
        if self.result_variable is not None and len(self.result_variable) > 0:
            return self.result_variable

        escaped_spec_name = task.task_spec.name.replace('-', '_')

        return f'spiff__{escaped_spec_name}_result'

    def _execute(self, task):
        def evaluate(param):
            try:
                param['value'] = task.workflow.script_engine.evaluate(task,
                        param['value'])
            except:
                pass

            return param

        operation_params_var_name = 'spiff__operation_params'
        evaluated_params = {k: evaluate(v) for k, v in self.operation_params.items()}
        script = f'ServiceTaskDelegate.call_connector("{self.operation_name}", {operation_params_var_name})'

        result = task.workflow.script_engine.evaluate_service_task_script(task, script, task.data,
                external_methods={ operation_params_var_name: evaluated_params })

        parsed_result = json.loads(result)

        task.data[self._result_variable(task)] = parsed_result
