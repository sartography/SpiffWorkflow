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


class Trigger(TaskSpec):

    """
    This class implements a task that triggers an event on another
    task.
    If more than one input is connected, the task performs an implicit
    multi merge.
    If more than one output is connected, the task performs an implicit
    parallel split.
    """

    def __init__(self, wf_spec, name, context, times=1, **kwargs):
        """
        Constructor.

        :type  wf_spec: WorkflowSpec
        :param wf_spec: A reference to the workflow specification.
        :type  name: str
        :param name: The name of the task spec.
        :type  context: list(str)
        :param context: A list of the names of tasks that are to be triggered.
        :type  times: int or :class:`SpiffWorkflow.operators.Term`
        :param times: The number of signals before the trigger fires.
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.TaskSpec`.
        """
        assert wf_spec is not None
        assert name is not None
        assert context is not None
        assert isinstance(context, list)
        TaskSpec.__init__(self, wf_spec, name, **kwargs)
        self.context = context
        self.times = times
        self.queued = 0

    def _on_trigger(self, my_task):
        """
        Enqueue a trigger, such that this tasks triggers multiple times later
        when _on_complete() is called.
        """
        self.queued += 1
        # All tasks that have already completed need to be put back to
        # READY.
        for thetask in my_task.workflow.task_tree:
            if thetask.thread_id != my_task.thread_id:
                continue
            if (thetask.task_spec == self and
                    thetask._has_state(TaskState.COMPLETED)):
                thetask._set_state(TaskState.FUTURE)
                thetask._ready()

    def _on_complete_hook(self, my_task):
        """
        A hook into _on_complete() that does the task specific work.

        :type  my_task: Task
        :param my_task: A task in which this method is executed.
        :rtype:  bool
        :returns: True on success, False otherwise.
        """
        times = int(valueof(my_task, self.times, 1)) + self.queued
        for i in range(times):
            for task_name in self.context:
                task = my_task.workflow.get_task_spec_from_name(task_name)
                task._on_trigger(my_task)
        self.queued = 0
        TaskSpec._on_complete_hook(self, my_task)

    def serialize(self, serializer):
        return serializer.serialize_trigger(self)

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state, **kwargs):
        """
        Deserializes the trigger using the provided serializer.
        """
        return serializer.deserialize_trigger(wf_spec,
                                              s_state,
                                              **kwargs)
