# Copyright (C) 2023 Sartography
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

import json
from copy import deepcopy

from SpiffWorkflow.bpmn.specs.mixins.service_task import ServiceTask
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskException

class ServiceTask(ServiceTask):

    def __init__(self, wf_spec, name, operation_name, operation_params, result_variable, **kwargs):
        super().__init__(wf_spec, name, **kwargs)
        self.operation_name = operation_name
        self.operation_params = operation_params
        self.result_variable = result_variable

    @property
    def spec_type(self):
        return 'Service Task'

    def _result_variable(self, task):
        if self.result_variable is not None and len(self.result_variable) > 0:
            return self.result_variable

        escaped_spec_name = task.task_spec.name.replace('-', '_')

        return f'spiff__{escaped_spec_name}_result'

    def _execute(self, task):
        def evaluate(param):
            param['value'] = task.workflow.script_engine.evaluate(task, param['value'])
            return param

        operation_params_copy = deepcopy(self.operation_params)
        evaluated_params = {k: evaluate(v) for k, v in operation_params_copy.items()}

        try:
            result = task.workflow.script_engine.call_service(self.operation_name,
                    evaluated_params, task.data)
        except Exception as e:
            wte = WorkflowTaskException("Error executing Service Task",
                                        task=task, exception=e)
            wte.add_note(str(e))
            raise wte
        parsed_result = json.loads(result)
        task.data[self._result_variable(task)] = parsed_result
        return True
