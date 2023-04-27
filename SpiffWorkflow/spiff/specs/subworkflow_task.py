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

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.specs.SubWorkflowTask import (
    SubWorkflowTask as DefaultSubWorkflow,
    TransactionSubprocess as DefaultTransaction,
    CallActivity as DefaultCallActivity,
)
from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask


class SubWorkflowTask(DefaultSubWorkflow, SpiffBpmnTask):

    def __init__(self, wf_spec, name, subworkflow_spec, transaction=False, **kwargs):

        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        # We don't so much as a class hierachy as a class pile and I'm giving up doing
        # this properly
        self.spec = subworkflow_spec
        self.transaction = transaction
        self.in_assign = []
        self.out_assign = []

    def _update_hook(self, my_task):
        # Don't really like duplicating this, but we need to run SpiffBpmn update rather than the default
        wf = my_task.workflow._get_outermost_workflow(my_task)
        subprocess = wf.subprocesses.get(my_task.id)
        if subprocess is None:
            super()._update_hook(my_task)
            self.create_workflow(my_task)
            self.start_workflow(my_task)
            my_task._set_state(TaskState.WAITING)
        else:
            return subprocess.is_completed()

    def _on_complete_hook(self, my_task):
        SpiffBpmnTask._on_complete_hook(self, my_task)

    @property
    def spec_type(self):
        return 'Subprocess'


class TransactionSubprocess(SubWorkflowTask, DefaultTransaction):

    def __init__(self, wf_spec, name, subworkflow_spec, transaction=True, **kwargs):

        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        self.spec = subworkflow_spec
        self.transaction = transaction
        self.in_assign = []
        self.out_assign = []

    @property
    def spec_type(self):
        return 'Transactional Subprocess'


class CallActivity(SubWorkflowTask, DefaultCallActivity):

    def __init__(self, wf_spec, name, subworkflow_spec, **kwargs):
        
        SpiffBpmnTask.__init__(self, wf_spec, name, **kwargs)
        self.spec = subworkflow_spec
        self.in_assign = []
        self.out_assign = []

    @property
    def spec_type(self):
        return 'Call Activity'
