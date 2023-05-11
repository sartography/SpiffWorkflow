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

from copy import deepcopy

from SpiffWorkflow.exceptions import SpiffWorkflowException
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.specs.mixins.bpmn_spec_mixin import BpmnSpecMixin


class SpiffBpmnTask(BpmnSpecMixin):

    def __init__(self, wf_spec, name, prescript=None, postscript=None, **kwargs):
        super().__init__(wf_spec, name, **kwargs)
        self.prescript = prescript
        self.postscript = postscript

    @property
    def spec_type(self):
        return 'Spiff BPMN Task'

    def execute_script(self, my_task, script):
        try:
            my_task.workflow.script_engine.execute(my_task, script)
        except Exception as exc:
            my_task._set_state(TaskState.ERROR)
            raise exc

    def get_payload(self, my_task, script, expr):
        try:
            data = deepcopy(my_task.data)
            my_task.worklflow.script_engine.execute(my_task, script, data)
            return my_task.workflow.script_engine._evaluate(expr, data)
        except Exception as exc:
            my_task._set_state(TaskState.WAITING)
            raise exc

    def _update_hook(self, my_task):
        super()._update_hook(my_task)
        if self.prescript is not None:
            try:
                self.execute_script(my_task, self.prescript)
            except SpiffWorkflowException as se:
                se.add_note("Error occurred in the Pre-Script")
                raise se
        return True

    def _on_complete_hook(self, my_task):
        if self.postscript is not None:
            try:
                self.execute_script(my_task, self.postscript)
            except SpiffWorkflowException as se:
                se.add_note("Error occurred in the Post-Script")
                raise se
        super()._on_complete_hook(my_task)
