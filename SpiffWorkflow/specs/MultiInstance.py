# -*- coding: utf-8 -*-

from builtins import range
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
from ..task import TaskState
from .base import TaskSpec
from ..operators import valueof


class MultiInstance(TaskSpec):

    """
    When executed, this task performs a split on the current task.
    The number of outgoing tasks depends on the runtime value of a
    specified data field.
    If more than one input is connected, the task performs an implicit
    multi merge.

    This task has one or more inputs and may have any number of outputs.
    """

    def __init__(self, wf_spec, name, times, **kwargs):
        """
        Constructor.

        :type  wf_spec: WorkflowSpec
        :param wf_spec: A reference to the workflow specification.
        :type  name: str
        :param name: The name of the task spec.
        :type  times: int or :class:`SpiffWorkflow.operators.Term`
        :param times: The number of tasks to create.
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.TaskSpec`.
        """
        if times is None:
            raise ValueError('times argument is required')
        TaskSpec.__init__(self, wf_spec, name, **kwargs)
        self.times = times
        self.prevtaskclass = None

    def _find_my_task(self, task):
        for thetask in task.workflow.task_tree:
            if thetask.thread_id != task.thread_id:
                continue
            if thetask.task_spec == self:
                return thetask
        return None

    def _on_trigger(self, task_spec):
        """
        May be called after execute() was already completed to create an
        additional outbound task.
        """
        # Find a Task for this TaskSpec.
        my_task = self._find_my_task(task_spec)
        if my_task._has_state(TaskState.COMPLETED):
            state = TaskState.READY
        else:
            state = TaskState.FUTURE
        for output in self.outputs:
            new_task = my_task._add_child(output, state)
            new_task.triggered = True
            output._predict(new_task)

    def _get_predicted_outputs(self, my_task):
        split_n = int(valueof(my_task, self.times, 1))

        # Predict the outputs.
        outputs = []
        for i in range(split_n):
            outputs += self.outputs
        return outputs

    def _predict_hook(self, my_task):
        split_n = int(valueof(my_task, self.times, 1))
        my_task._set_internal_data(splits=split_n)

        # Create the outgoing tasks.
        outputs = []
        for i in range(split_n):
            outputs += self.outputs
        if my_task._is_definite():
            my_task._sync_children(outputs, TaskState.FUTURE)
        else:
            my_task._sync_children(outputs, TaskState.LIKELY)

    def _on_complete_hook(self, my_task):
        outputs = self._get_predicted_outputs(my_task)
        my_task._sync_children(outputs, TaskState.FUTURE)
        for child in my_task.children:
            child.task_spec._update(child)

    def serialize(self, serializer):
        return serializer.serialize_multi_instance(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_multi_instance(wf_spec, s_state)
