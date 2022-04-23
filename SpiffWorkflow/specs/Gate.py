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
from ..task import TaskState
from .base import TaskSpec


class Gate(TaskSpec):

    """
    This class implements a task that can only execute when another
    specified task is completed.
    If more than one input is connected, the task performs an implicit
    multi merge.
    If more than one output is connected, the task performs an implicit
    parallel split.
    """

    def __init__(self, wf_spec, name, context, **kwargs):
        """
        Constructor.

        :type  wf_spec: WorkflowSpec
        :param wf_spec: A reference to the workflow specification.
        :type  name: str
        :param name: The name of the task spec.
        :type  context: str
        :param context: The name of the task that needs to complete before
                        this task can execute.
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.TaskSpec`.
        """
        assert wf_spec is not None
        assert name is not None
        assert context is not None
        TaskSpec.__init__(self, wf_spec, name, **kwargs)
        self.context = context

    def _update_hook(self, my_task):
        context_task = my_task.workflow.get_task_spec_from_name(self.context)
        root_task = my_task.workflow.task_tree
        for task in root_task._find_any(context_task):
            if task.thread_id != my_task.thread_id:
                continue
            if not task._has_state(TaskState.COMPLETED):
                my_task._set_state(TaskState.WAITING)
                return
        super(Gate, self)._update_hook(my_task)

    def serialize(self, serializer):
        return serializer.serialize_gate(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_gate(wf_spec, s_state)
