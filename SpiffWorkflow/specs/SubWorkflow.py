# -*- coding: utf-8 -*-

# Copyright (C) 2007 Samuel Abels
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA
import os

from . import StartTask
from .base import TaskSpec
from ..task import TaskState
from ..exceptions import WorkflowException
from ..operators import valueof


class SubWorkflow(TaskSpec):

    """
    A SubWorkflow is a task that wraps a WorkflowSpec, such that you can
    re-use it in multiple places as if it were a task.
    If more than one input is connected, the task performs an implicit
    multi merge.
    If more than one output is connected, the task performs an implicit
    parallel split.
    """

    def __init__(self,
                 wf_spec,
                 name,
                 file,
                 in_assign=None,
                 out_assign=None,
                 **kwargs):
        """
        Constructor.

        :type  wf_spec: WorkflowSpec
        :param wf_spec: A reference to the workflow specification.
        :type  name: str
        :param name: The name of the task spec.
        :type  file: str
        :param file: The name of a file containing a workflow.
        :type  in_assign: list(str)
        :param in_assign: The names of data fields to carry over.
        :type  out_assign: list(str)
        :param out_assign: The names of data fields to carry back.
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.TaskSpec`.
        """
        assert wf_spec is not None
        assert name is not None
        super(SubWorkflow, self).__init__(wf_spec, name, **kwargs)
        self.file = None
        self.in_assign = in_assign is not None and in_assign or []
        self.out_assign = out_assign is not None and out_assign or []
        if file is not None:
            dirname = os.path.dirname(wf_spec.file)
            self.file = os.path.join(dirname, file)

    def test(self):
        TaskSpec.test(self)
        if self.file is not None and not os.path.exists(self.file):
            raise WorkflowException(
                self, 'File does not exist: %s' % self.file)

    def _predict_hook(self, my_task):
        outputs = [task.task_spec for task in my_task.children]
        for output in self.outputs:
            if output not in outputs:
                outputs.insert(0, output)
        if my_task._is_definite():
            my_task._sync_children(outputs, TaskState.FUTURE)
        else:
            my_task._sync_children(outputs, my_task.state)

    def _create_subworkflow(self, my_task):
        from ..serializer.prettyxml import XmlSerializer
        from ..specs import WorkflowSpec
        from ..workflow import Workflow
        file_name = valueof(my_task, self.file)
        serializer = XmlSerializer()
        with open(file_name) as fp:
            xml = fp.read()
        wf_spec = WorkflowSpec.deserialize(
            serializer, xml, filename=file_name)
        outer_workflow = my_task.workflow.outer_workflow
        return Workflow(wf_spec, parent=outer_workflow)

    def _on_ready_before_hook(self, my_task):
        subworkflow = self._create_subworkflow(my_task)
        subworkflow.completed_event.connect(
            self._on_subworkflow_completed, my_task)
        self._integrate_subworkflow_tree(my_task, subworkflow)
        my_task._set_internal_data(subworkflow=subworkflow)

    def _integrate_subworkflow_tree(self, my_task, subworkflow):
        # Integrate the tree of the subworkflow into the tree of this workflow.
        my_task._sync_children(self.outputs, TaskState.FUTURE)
        for child in my_task.children:
            child.task_spec._update(child)
            child._inherit_data()
        for child in subworkflow.task_tree.children:
            my_task.children.insert(0, child)
            child.parent = my_task

    def _on_ready_hook(self, my_task):
        # Assign variables, if so requested.
        subworkflow = my_task._get_internal_data('subworkflow')
        for child in subworkflow.task_tree.children:
            for assignment in self.in_assign:
                assignment.assign(my_task, child)

        self._predict(my_task)
        for child in subworkflow.task_tree.children:
            child.task_spec._update(child)

    def _on_subworkflow_completed(self, subworkflow, my_task):
        # Assign variables, if so requested.
        for child in my_task.children:
            if not isinstance(child.task_spec, StartTask):
                if subworkflow.last_task is not None:
                    child.data = subworkflow.last_task.data
                for assignment in self.out_assign:
                    assignment.assign(subworkflow, child)

                # Alright, abusing that hook is just evil but it works.
                child.task_spec._update_hook(child)

    def _on_complete_hook(self, my_task):
        for child in my_task.children:
            if isinstance(child.task_spec, StartTask):
                child.task_spec._update(child)

    def serialize(self, serializer):
        return serializer.serialize_sub_workflow(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_sub_workflow(wf_spec, s_state)
