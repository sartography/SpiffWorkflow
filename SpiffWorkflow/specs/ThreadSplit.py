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
from SpiffWorkflow.specs.ThreadStart import ThreadStart

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
                 parent,
                 name,
                 times = None,
                 times_attribute = None,
                 suppress_threadstart_creation = False,
                 **kwargs):
        """
        Constructor.
        
        :type  parent: :class:`SpiffWorkflow.specs.WorkflowSpec`
        :param parent: A reference to the parent (usually a workflow).
        :type  name: string
        :param name: A name for the task.
        :type  times: int or None
        :param times: The number of tasks to create.
        :type  times_attribute: str or None
        :param times_attribute: The name of a data field that specifies
                                the number of outgoing tasks.
        :type  suppress_threadstart_creation: bool
        :param suppress_threadstart_creation: Don't create a ThreadStart, because
                                              the deserializer is about to.
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.TaskSpec`.
        """
        if not times_attribute and not times:
            raise ValueError('require times or times_attribute argument')
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.times_attribute = times_attribute
        self.times           = times
        if not suppress_threadstart_creation:
            self.thread_starter  = ThreadStart(parent, **kwargs)
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

    def _find_my_task(self, workflow):
        for task in workflow.branch_tree:
            if task.thread_id != my_task.thread_id:
                continue
            if task.task == self:
                return task
        return None

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
        # Find a Task for this task.
        my_task = self._find_my_task(my_task.workflow)
        for output in self.outputs:
            new_task = my_task.add_child(output, Task.READY)
            new_task.triggered = True

    def _predict_hook(self, my_task):
        split_n = my_task.get_data('split_n', self.times)
        if split_n is None:
            split_n = my_task.get_data(self.times_attribute, 1)

        # if we were created with thread_starter suppressed, connect it now.
        if self.thread_starter is None:
            self.thread_starter = self.outputs[0]

        # Predict the outputs.
        outputs = []
        for i in range(split_n):
            outputs.append(self.thread_starter)
        if my_task._is_definite():
            my_task._sync_children(outputs, Task.FUTURE)
        else:
            my_task._sync_children(outputs, Task.LIKELY)

    def _on_complete_hook(self, my_task):
        # Split, and remember the number of splits in the context data.
        split_n = self.times
        if split_n is None:
            split_n = my_task.get_data(self.times_attribute)

        # Create the outgoing tasks.
        outputs = []
        for i in range(split_n):
            outputs.append(self.thread_starter)
        my_task._sync_children(outputs, Task.FUTURE)
        for child in my_task.children:
            child.task_spec._update(child)

    def serialize(self, serializer):
        return serializer._serialize_thread_split(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer._deserialize_thread_split(wf_spec, s_state)
