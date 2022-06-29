# -*- coding: utf-8 -*-
from copy import deepcopy

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.exceptions import WorkflowDataException
from .BpmnSpecMixin import BpmnSpecMixin
from ...specs.SubWorkflow import SubWorkflow
from ...specs import TaskSpec


class SubWorkflowTask(SubWorkflow, BpmnSpecMixin):

    """
    Task Spec for a bpmn node containing a subworkflow.
    """
    def __init__(self, wf_spec, name, subworkflow_spec, transaction=False, **kwargs):
        """
        Constructor.

        :param bpmn_wf_spec: the BpmnProcessSpec for the sub process.
        :param bpmn_wf_class: the BpmnWorkflow class to instantiate
        """
        super(SubWorkflowTask, self).__init__(wf_spec, name, None, **kwargs)
        self.spec = subworkflow_spec
        self.transaction = transaction

    def test(self):
        TaskSpec.test(self)

    def _on_ready_before_hook(self, my_task):
        subworkflow = my_task.workflow.create_subprocess(my_task, self.spec, self.name)
        subworkflow.completed_event.connect(self._on_subworkflow_completed, my_task)
        subworkflow.data = deepcopy(my_task.workflow.data)

    def _on_ready_hook(self, my_task):

        subworkflow = my_task.workflow.get_subprocess(my_task)
        start = subworkflow.get_tasks_from_spec_name('Start', workflow=subworkflow)

        if len(subworkflow.spec.data_inputs) == 0:
            # Copy all task data into start taak if no inputs specified
            start[0].set_data(**my_task.data)
        else:
            # Copy only task data with the specified names
            data = {}
            for var in subworkflow.spec.data_inputs:
                if var.name not in my_task.data:
                    raise WorkflowDataException(my_task, data_input=var)
                data[var.name] = deepcopy(my_task.data[var.name])
            start[0].set_data(**data)

        self._predict(my_task)
        for child in subworkflow.task_tree.children:
            child.task_spec._update(child)

        my_task._set_state(TaskState.WAITING)

    def _on_subworkflow_completed(self, subworkflow, my_task):

        super(SubWorkflowTask, self)._on_subworkflow_completed(subworkflow, my_task)
        # Shouldn't this always be true?
        if isinstance(my_task.parent.task_spec, BpmnSpecMixin):
            my_task.parent.task_spec._child_complete_hook(my_task)

        if len(subworkflow.spec.data_outputs) == 0:
            # Copy all workflow data if no outputs are specified
            my_task.data = deepcopy(subworkflow.data)
        else:
            # Update the task data with only the specified workflow data
            data = {}
            for var in subworkflow.spec.data_outputs:
                # Copy data out of workflow if specified
                if var.name not in subworkflow.data:
                    raise WorkflowDataException(my_task, data_output=var)
                data[var.name] = subworkflow.data[var.name]
            my_task.update_data(data)

        my_task._set_state(TaskState.READY)

    def _update_hook(self, my_task):
        wf = my_task.workflow._get_outermost_workflow(my_task)
        if my_task.id not in wf.subprocesses:
            super()._update_hook(my_task)

    def _on_complete_hook(self, my_task):
        for child in my_task.children:
            child.task_spec._update(child)

    def _on_cancel(self, my_task):
        subworkflow = my_task.workflow.get_subprocess(my_task)
        if subworkflow is not None:
            subworkflow.cancel()

    def serialize(self, serializer):
        return serializer.serialize_subworkflow_task(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_subworkflow_task(wf_spec, s_state, SubWorkflowTask)


class CallActivity(SubWorkflowTask):

    def __init__(self, wf_spec, name, subworkflow_spec, **kwargs):
        super(CallActivity, self).__init__(wf_spec, name, subworkflow_spec, False, **kwargs)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_subworkflow_task(wf_spec, s_state, CallActivity)

class TransactionSubprocess(SubWorkflowTask):

    def __init__(self, wf_spec, name, subworkflow_spec, **kwargs):
        super(TransactionSubprocess, self).__init__(wf_spec, name, subworkflow_spec, True, **kwargs)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_subworkflow_task(wf_spec, s_state, TransactionSubprocess)
