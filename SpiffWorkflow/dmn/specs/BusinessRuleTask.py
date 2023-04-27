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

from SpiffWorkflow.exceptions import WorkflowTaskException, SpiffWorkflowException

from ...specs.Simple import Simple

from ...bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from ...util.deep_merge import DeepMerge


class BusinessRuleTask(Simple, BpmnSpecMixin):
    """
    Task Spec for a bpmn:businessTask (DMB Decision Reference) node.
    """

    def _on_trigger(self, my_task):
        pass

    def __init__(self, wf_spec, name, dmnEngine, **kwargs):
        super().__init__(wf_spec, name, **kwargs)
        self.dmnEngine = dmnEngine
        self.resDict = None

    @property
    def spec_class(self):
        return 'Business Rule Task'

    def _run_hook(self, my_task):
        try:
            my_task.data = DeepMerge.merge(my_task.data, self.dmnEngine.result(my_task))
            super(BusinessRuleTask, self)._run_hook(my_task)
        except SpiffWorkflowException as we:
            we.add_note(f"Business Rule Task '{my_task.task_spec.description}'.")
            raise we
        except Exception as e:
            error = WorkflowTaskException(str(e), task=my_task)
            error.add_note(f"Business Rule Task '{my_task.task_spec.description}'.")
            raise error
        return True
