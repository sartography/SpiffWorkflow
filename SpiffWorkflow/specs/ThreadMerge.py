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
from ..exceptions import WorkflowException
from ..operators import valueof
from ..specs import Join


class ThreadMerge(Join):

    """
    This class represents a task for synchronizing branches that were
    previously split using a a ThreadSplit.
    It has two or more incoming branches and one or more outputs.
    """

    def __init__(self,
                 wf_spec,
                 name,
                 split_task,
                 **kwargs):
        """
        Constructor.

        :type  wf_spec: :class:`SpiffWorkflow.specs.WorkflowSpec`
        :param wf_spec: A reference to the parent (usually a workflow).
        :type  name: string
        :param name: A name for the task.
        :type  split_task: str
        :param split_task: The name of the task spec that was previously
                           used to split the branch.
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.Join`.
        """
        assert split_task is not None
        Join.__init__(self, wf_spec, name, split_task, **kwargs)

    def _start(self, my_task):
        # If the threshold was already reached, there is nothing else to do.
        if my_task._has_state(TaskState.COMPLETED):
            return False
        if my_task._has_state(TaskState.READY):
            return True

        # Retrieve a list of all activated tasks from the associated
        # task that did the conditional parallel split.
        split_task = my_task._find_ancestor_from_name(self.split_task)
        if split_task is None:
            msg = 'Join with %s, which was not reached' % self.split_task
            raise WorkflowException(self, msg)
        tasks = split_task.task_spec._get_activated_threads(split_task)

        # The default threshold is the number of threads that were started.
        threshold = valueof(my_task, self.threshold)
        if threshold is None:
            threshold = len(tasks)

        # Look up which tasks have already completed.
        waiting_tasks = []
        completed = 0
        for task in tasks:
            # Refresh path prediction.
            task.task_spec._predict(task)

            if self._branch_is_complete(task):
                completed += 1
            else:
                waiting_tasks.append(task)

        # If the threshold was reached, get ready to fire.
        if completed >= threshold:
            # If this is a cancelling join, cancel all incoming branches,
            # except for the one that just completed.
            if self.cancel_remaining:
                for task in waiting_tasks:
                    task.cancel()
            return True

        # We do NOT set the task state to COMPLETED, because in
        # case all other incoming tasks get cancelled (or never reach
        # the ThreadMerge for other reasons, such as reaching a stub branch),
        # we need to revisit it.
        return False

    def _update_hook(self, my_task):
        if not self._start(my_task):
            my_task._set_state(TaskState.WAITING)
            return

        split_task_spec = my_task.workflow.get_task_spec_from_name(
            self.split_task)
        split_task = my_task._find_ancestor(split_task_spec)

        # Find the inbound task that was completed last.
        last_changed = None
        tasks = []
        for task in split_task._find_any(self):
            if self.split_task and task._is_descendant_of(my_task):
                continue
            changed = task.parent.last_state_change
            if last_changed is None \
                    or changed > last_changed.parent.last_state_change:
                last_changed = task
            tasks.append(task)

        # Mark all tasks in this thread that reference this task as
        # completed, except for the first one, which should be READY.
        for task in tasks:
            if task == last_changed:
                self.entered_event.emit(my_task.workflow, my_task)
                task._ready()
            else:
                task._set_state(TaskState.COMPLETED)
                task._drop_children()

    def serialize(self, serializer):
        return serializer.serialize_thread_merge(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_thread_merge(wf_spec, s_state)
