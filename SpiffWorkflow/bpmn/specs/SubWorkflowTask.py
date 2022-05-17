# -*- coding: utf-8 -*-
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

    def _on_subworkflow_completed(self, subworkflow, my_task):
        super(SubWorkflowTask, self)._on_subworkflow_completed(subworkflow, my_task)
        if isinstance(my_task.parent.task_spec, BpmnSpecMixin):
            my_task.parent.task_spec._child_complete_hook(my_task)

    def _on_ready_before_hook(self, my_task):
        subworkflow = my_task.workflow.create_subprocess(my_task, self.spec, self.name)
        subworkflow.completed_event.connect(self._on_subworkflow_completed, my_task)
        subworkflow.data = my_task.workflow.data
        self._integrate_subworkflow_tree(my_task, subworkflow)

    def _on_ready_hook(self, my_task):
        # Assign variables, if so requested.
        subworkflow = my_task.workflow.get_subprocess(my_task)
        for child in subworkflow.task_tree.children:
            for assignment in self.in_assign:
                assignment.assign(my_task, child)

        self._predict(my_task)
        for child in subworkflow.task_tree.children:
            child.task_spec._update(child)

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
