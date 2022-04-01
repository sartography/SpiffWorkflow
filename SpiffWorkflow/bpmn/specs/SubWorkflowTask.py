# -*- coding: utf-8 -*-


from .BpmnSpecMixin import BpmnSpecMixin
from ...specs.SubWorkflow import SubWorkflow
from ...specs import TaskSpec


class SubWorkflowTask(SubWorkflow, BpmnSpecMixin):

    """
    Task Spec for a bpmn node containing a subworkflow.
    """

    def __init__(self, wf_spec, name, bpmn_wf_spec=None, bpmn_wf_class=None, transaction=False,
                 **kwargs):
        """
        Constructor.

        :param bpmn_wf_spec: the BpmnProcessSpec for the sub process.
        :param bpmn_wf_class: the BpmnWorkflow class to instantiate
        """
        super(SubWorkflowTask, self).__init__(wf_spec, name, None, **kwargs)
        self.spec = bpmn_wf_spec
        self.wf_class = bpmn_wf_class
        self.transaction = transaction
        self.sub_workflow = None

    def test(self):
        TaskSpec.test(self)

    def create_sub_workflow(self, my_task):

        sub_workflow = self.wf_class(
            self.spec, name=self.name,
            read_only=my_task.workflow.read_only,
            script_engine=my_task.workflow.outer_workflow.script_engine,
            parent=my_task.workflow)

        sub_workflow.completed_event.connect(
            self._on_subworkflow_completed, my_task)
        sub_workflow.data = my_task.workflow.data
        return sub_workflow

    def get_workflow_class(self):
        """
        Returns the workflow class to instantiate for the sub workflow
        """
        return self.wf_class

    def _on_subworkflow_completed(self, subworkflow, my_task):
        super(SubWorkflowTask, self)._on_subworkflow_completed(
            subworkflow, my_task)
        if isinstance(my_task.parent.task_spec, BpmnSpecMixin):
            my_task.parent.task_spec._child_complete_hook(my_task)

    def _on_ready_before_hook(self, my_task):
        self.sub_workflow = self.create_sub_workflow(my_task)
        self._integrate_subworkflow_tree(my_task, self.sub_workflow)

    def _on_ready_hook(self, my_task):
        # Assign variables, if so requested.
        for child in self.sub_workflow.task_tree.children:
            for assignment in self.in_assign:
                assignment.assign(my_task, child)

        self._predict(my_task)
        for child in self.sub_workflow.task_tree.children:
            child.task_spec._update(child)

    def serialize(self, serializer):
        return serializer.serialize_subworkflow_task(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_subworkflow_task(wf_spec, s_state, SubWorkflowTask)


class CallActivity(SubWorkflowTask):

    def __init__(self, wf_spec, name, bpmn_wf_spec=None, bpmn_wf_class=None, **kwargs):
        super(CallActivity, self).__init__(wf_spec, name, bpmn_wf_spec, bpmn_wf_class, False, **kwargs)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_subworkflow_task(wf_spec, s_state, CallActivity)

class TransactionSubprocess(SubWorkflowTask):

    def __init__(self, wf_spec, name, bpmn_wf_spec=None, bpmn_wf_class=None, **kwargs):
        super(TransactionSubprocess, self).__init__(wf_spec, name, bpmn_wf_spec, bpmn_wf_class, True, **kwargs)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_subworkflow_task(wf_spec, s_state, TransactionSubprocess)
