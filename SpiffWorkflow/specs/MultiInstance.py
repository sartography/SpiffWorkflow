# -*- coding: utf-8 -*-
from __future__ import division
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
from SpiffWorkflow.Task import Task
from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.specs.TaskSpec import TaskSpec
from SpiffWorkflow.operators import valueof

class MultiInstance(TaskSpec):
    """
    When executed, this task performs a split on the current task.
    The number of outgoing tasks depends on the runtime value of a
    specified data field.
    If more than one input is connected, the task performs an implicit
    multi merge.

    This task has one or more inputs and may have any number of outputs.
    """

    def __init__(self, parent, name, times = None, **kwargs):
        """
        Constructor.
        
        :type  parent: TaskSpec
        :param parent: A reference to the parent task spec.
        :type  name: str
        :param name: The name of the task spec.
        :type  times: int
        :param times: The number of tasks to create.
        :type  kwargs: dict
        :param kwargs: See L{SpiffWorkflow.specs.TaskSpec}.
        """
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.times = times

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
        if my_task._has_state(Task.COMPLETED):
            state = Task.READY
        else:
            state = Task.FUTURE
        for output in self.outputs:
            new_task = my_task._add_child(output, state)
            new_task.triggered = True
            output._predict(new_task)

    def _get_predicted_outputs(self, my_task):
        split_n = my_task._get_internal_data('splits', 1)

        # Predict the outputs.
        outputs = []
        for i in range(split_n):
            outputs += self.outputs
        return outputs

    def _predict_hook(self, my_task):
        split_n = valueof(my_task, self.times)
        if split_n is None:
            return
        my_task._set_internal_data(splits = split_n)

        # Create the outgoing tasks.
        outputs = []
        for i in range(split_n):
            outputs += self.outputs
        if my_task._is_definite():
            my_task._sync_children(outputs, Task.FUTURE)
        else:
            my_task._sync_children(outputs, Task.LIKELY)

    def _on_complete_hook(self, my_task):
        outputs = self._get_predicted_outputs(my_task)
        my_task._sync_children(outputs, Task.FUTURE)
        for child in my_task.children:
            child.task_spec._update_state(child)

    def serialize(self, serializer):
        return serializer._serialize_multi_instance(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer._deserialize_multi_instance(wf_spec, s_state)
