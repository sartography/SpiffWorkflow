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
        if result_variable is None or result_variable == '':
            self.result_variable = f'spiff__{name.replace("-", "_")}_result'
        else:
            self.result_variable = result_variable

    def evalutate_params(self, task):
        evaluated_params = {}
        for name, param in self.operation_params.items():
            evaluated_params[name] = {
                'value': task.workflow.script_engine.evaluate(task, param['value']),
                'type': param['type'],
            }
        return evaluated_params

    def _execute(self, task):
        result = task.workflow.script_engine.call_service(
            task,
            operation_name=self.operation_name,
            operation_params=self.evalutate_params(task),
        )
        task.data[self.result_variable] = json.loads(result)
        return True
