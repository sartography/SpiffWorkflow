import json
from SpiffWorkflow.bpmn.specs.ServiceTask import ServiceTask
from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask

class ServiceTask(SpiffBpmnTask, ServiceTask):

    def __init__(self, wf_spec, name, operation_name, operation_params, **kwargs):
        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        self.operation_name = operation_name
        self.operation_params = operation_params
        # TODO parse this from bpmn
        self.result_variable = None

    def _result_variable(self, task):
        if self.result_variable is not None:
            return self.reslut_variable

        return f'spiff__{task.task_spec.name}_result'

    def _execute(self, task):
        def evaluate(expression):
            return task.workflow.script_engine.evaluate(task, repr(expression))

        operation_params_var_name = 'spiff__operation_params'
        evaluated_params = {k: evaluate(v) for k, v in self.operation_params.items()}
        script = f'ServiceTaskDelegate.call_connector("{self.operation_name}", {operation_params_var_name})'

        result = task.workflow.script_engine.evaluate_service_task_script(task, script, task.data,
                external_methods={ operation_params_var_name: evaluated_params })

        parsed_result = json.loads(result)

        task.data[self._result_variable(task)] = parsed_result
