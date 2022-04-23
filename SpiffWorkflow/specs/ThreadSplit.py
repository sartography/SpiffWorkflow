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
from .ThreadStart import ThreadStart
from ..operators import valueof


class ThreadSplit(TaskSpec):

    """
    When executed, this task performs a split on the current my_task.
    The number of outgoing my_tasks depends on the runtime value of a
    specified data field.
    If more than one input is connected, the task performs an implicit
    multi merge.

    This task has one or more inputs and may have any number of outputs.
    """

    def __init__(self,
                 wf_spec,
                 name,
                 times=1,
                 suppress_threadstart_creation=False,
                 **kwargs):
        """
        Constructor.

        :type  wf_spec: WorkflowSpec`
        :param wf_spec: A reference to the workflow specification.
        :type  name: string
        :param name: A name for the task.
        :type  times: int or :class:`SpiffWorkflow.operators.Term`
        :param times: The number of tasks to create.
        :type  suppress_threadstart_creation: bool
        :param suppress_threadstart_creation: Don't create a ThreadStart,
          because the deserializer is about to.
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.TaskSpec`.
        """
        if times is None:
            raise ValueError('times argument is required')
        TaskSpec.__init__(self, wf_spec, name, **kwargs)
        self.times = times
        if not suppress_threadstart_creation:
            self.thread_starter = ThreadStart(wf_spec, **kwargs)
            self.outputs.append(self.thread_starter)
            self.thread_starter._connect_notify(self)
        else:
            self.thread_starter = None

    def connect(self, task_spec):
        """
        Connect the *following* task to this one. In other words, the
        given task is added as an output task.

        task -- the task to connect to.
        """
        self.thread_starter.outputs.append(task_spec)
        task_spec._connect_notify(self.thread_starter)

    def _get_activated_tasks(self, my_task, destination):
        """
        Returns the list of tasks that were activated in the previous
        call of execute(). Only returns tasks that point towards the
        destination task, i.e. those which have destination as a
        descendant.

        my_task -- the task of this TaskSpec
        destination -- the child task
        """
        task = destination._find_ancestor(self.thread_starter)
        return self.thread_starter._get_activated_tasks(task, destination)

    def _get_activated_threads(self, my_task):
        """
        Returns the list of threads that were activated in the previous
        call of execute().

        my_task -- the task of this TaskSpec
        """
        return my_task.children

    def _on_trigger(self, my_task):
        """
        May be called after execute() was already completed to create an
        additional outbound task.
        """
        for output in self.outputs:
            new_task = my_task.add_child(output, TaskState.READY)
            new_task.triggered = True

    def _predict_hook(self, my_task):
        split_n = int(valueof(my_task, self.times))

        # if we were created with thread_starter suppressed, connect it now.
        if self.thread_starter is None:
            self.thread_starter = self.outputs[0]

        # Predict the outputs.
        outputs = []
        for i in range(split_n):
            outputs.append(self.thread_starter)
        if my_task._is_definite():
            my_task._sync_children(outputs, TaskState.FUTURE)
        else:
            my_task._sync_children(outputs, TaskState.LIKELY)

    def _on_complete_hook(self, my_task):
        # Split, and remember the number of splits in the context data.
        split_n = int(valueof(my_task, self.times))

        # Create the outgoing tasks.
        outputs = []
        for i in range(split_n):
            outputs.append(self.thread_starter)
        my_task._sync_children(outputs, TaskState.FUTURE)
        for child in my_task.children:
            child.task_spec._update(child)

    def serialize(self, serializer):
        return serializer.serialize_thread_split(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_thread_split(wf_spec, s_state)
