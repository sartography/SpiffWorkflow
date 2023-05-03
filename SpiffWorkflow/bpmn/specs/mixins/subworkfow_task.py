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

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.specs.base import TaskSpec
from SpiffWorkflow.bpmn.exceptions import WorkflowDataException


class SubWorkflowTask(TaskSpec):
    """
    Task Spec for a bpmn node containing a subworkflow.
    """
    def __init__(self, wf_spec, name, subworkflow_spec, transaction=False, **kwargs):
        """
        Constructor.

        :param bpmn_wf_spec: the BpmnProcessSpec for the sub process.
        :param bpmn_wf_class: the BpmnWorkflow class to instantiate
        """
        super(SubWorkflowTask, self).__init__(wf_spec, name, **kwargs)
        self.spec = subworkflow_spec
        self.transaction = transaction

    @property
    def spec_type(self):
        return 'Subprocess'

    def _on_subworkflow_completed(self, subworkflow, my_task):
        self.update_data(my_task, subworkflow)

    def _update_hook(self, my_task):
        wf = my_task.workflow._get_outermost_workflow(my_task)
        subprocess = wf.subprocesses.get(my_task.id)
        if subprocess is None:
            super()._update_hook(my_task)
            self.create_workflow(my_task)
            self.start_workflow(my_task)
            my_task._set_state(TaskState.WAITING)
        else:
            return subprocess.is_completed()

    def _on_cancel(self, my_task):
        subworkflow = my_task.workflow.get_subprocess(my_task)
        if subworkflow is not None:
            subworkflow.cancel()

    def copy_data(self, my_task, subworkflow):
        # There is only one copy of any given data object, so it should be updated immediately
        # Doing this is actually a little problematic, because it gives parent processes access to 
        # data objects defined in subprocesses.
        # But our data management is already hopelessly messed up and in dire needs of reconsideration
        if len(subworkflow.spec.data_objects) > 0:
            subworkflow.data = my_task.workflow.data
        start = subworkflow.get_tasks_from_spec_name('Start', workflow=subworkflow)
        start[0].set_data(**my_task.data)

    def update_data(self, my_task, subworkflow):
        my_task.data = deepcopy(subworkflow.last_task.data)

    def create_workflow(self, my_task):
        subworkflow = my_task.workflow.create_subprocess(my_task, self.spec, self.name)
        subworkflow.completed_event.connect(self._on_subworkflow_completed, my_task)

    def start_workflow(self, my_task):
        subworkflow = my_task.workflow.get_subprocess(my_task)
        self.copy_data(my_task, subworkflow)
        for child in subworkflow.task_tree.children:
            child.task_spec._update(child)
        my_task._set_state(TaskState.WAITING)

    def task_will_set_children_future(self, my_task):
        my_task.workflow.delete_subprocess(my_task)


class CallActivity(SubWorkflowTask):

    def __init__(self, wf_spec, name, subworkflow_spec, **kwargs):
        super(CallActivity, self).__init__(wf_spec, name, subworkflow_spec, False, **kwargs)

    def copy_data(self, my_task, subworkflow):

        start = subworkflow.get_tasks_from_spec_name('Start', workflow=subworkflow)
        if subworkflow.spec.io_specification is None or len(subworkflow.spec.io_specification.data_inputs) == 0:
            # Copy all task data into start task if no inputs specified
            start[0].set_data(**my_task.data)
        else:
            # Otherwise copy only task data with the specified names
            for var in subworkflow.spec.io_specification.data_inputs:
                if var.name not in my_task.data:
                    raise WorkflowDataException(
                        "You are missing a required Data Input for a call activity.",
                        task=my_task,
                        data_input=var,
                    )
                start[0].data[var.name] = my_task.data[var.name]

    def update_data(self, my_task, subworkflow):

        if subworkflow.spec.io_specification is None or len(subworkflow.spec.io_specification.data_outputs) == 0:
            # Copy all workflow data if no outputs are specified
            my_task.data = deepcopy(subworkflow.last_task.data)
        else:
            end = subworkflow.get_tasks_from_spec_name('End', workflow=subworkflow)
            # Otherwise only copy data with the specified names
            for var in subworkflow.spec.io_specification.data_outputs:
                if var.name not in end[0].data:
                    raise WorkflowDataException(
                        f"The Data Output was not available in the subprocess output.",
                        task=my_task,
                        data_output=var,
                    )
                my_task.data[var.name] = end[0].data[var.name]

    @property
    def spec_type(self):
        return 'Call Activity'


class TransactionSubprocess(SubWorkflowTask):

    def __init__(self, wf_spec, name, subworkflow_spec, **kwargs):
        super(TransactionSubprocess, self).__init__(wf_spec, name, subworkflow_spec, True, **kwargs)

    @property
    def spec_type(self):
        return 'Transactional Subprocess'

