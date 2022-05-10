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
from ..task import Task, TaskState
from ..exceptions import WorkflowException
from .base import TaskSpec
from ..operators import valueof


class Join(TaskSpec):

    """
    A task for synchronizing branches that were previously split using a
    conditional task, such as MultiChoice. It has two or more incoming
    branches and one or more outputs.

    Keep in mind that each Join spec may have multiple corresponding
    Task objects::

        - When using the MultiInstance task
        - When using the ThreadSplit task

    When using the MultiInstance pattern, Join works across all
    the resulting task instances. When using the ThreadSplit
    pattern, Join ignores instances from another thread.

    A Join task may enter the following states::

        - FUTURE, LIKELY, or MAYBE: These are the initial predicted states.

        - WAITING: This state is reached as soon as at least one of the
        predecessors has completed.

        - READY: All predecessors have completed. If multiple tasks within
        the thread reference the same Join (e.g. if MultiInstance is used),
        this state is only reached on one of the tasks; all other tasks go
        directly from WAITING to completed.

        - COMPLETED: All predecessors have completed, and
        :class:`Task.complete()` was called.

    The state may also change directly from WAITING to COMPLETED if the
    Trigger pattern is used.
    """

    def __init__(self,
                 wf_spec,
                 name,
                 split_task=None,
                 threshold=None,
                 cancel=False,
                 **kwargs):
        """
        Constructor.

        :type  wf_spec: :class:`SpiffWorkflow.specs.WorkflowSpec`
        :param wf_spec: A reference to the parent (usually a workflow).
        :type  name: string
        :param name: A name for the task.
        :type  split_task: str or None
        :param split_task: The name of the task spec that was previously
                           used to split the branch. If this is None,
                           the most recent branch split is merged.
        :type  threshold: int, :class:`SpiffWorkflow.operators.Attrib`, or None
        :param threshold: Specifies how many incoming branches need to
                          complete before the task triggers. When the limit
                          is reached, the task fires but still expects all
                          other branches to complete.
                          You may also pass an attribute, in which case
                          the value is resolved at runtime.
                          Passing None means all incoming branches.
        :type  cancel: bool
        :param cancel: When True, any remaining incoming branches are
                       cancelled as soon as the discriminator is activated.
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.TaskSpec`.
        """
        super(Join, self).__init__(wf_spec, name, **kwargs)
        self.split_task = split_task
        self.threshold = threshold
        self.cancel_remaining = cancel

    def _branch_is_complete(self, my_task):
        # Determine whether that branch is now completed by checking whether
        # it has any waiting items other than myself in it.
        skip = None
        for task in Task.Iterator(my_task, TaskState.NOT_FINISHED_MASK):
            # If the current task is a child of myself, ignore it.
            if skip is not None and task._is_descendant_of(skip):
                continue
            if task.task_spec == self:
                skip = task
                continue
            return False
        return True

    def _branch_may_merge_at(self, task):
        for child in task:
            # Ignore tasks that were created by a trigger.
            if child.triggered:
                continue
            # Merge found.
            if child.task_spec == self:
                return True
            # If the task is predicted with less outputs than he has
            # children, that means the prediction may be incomplete (for
            # example, because a prediction is not yet possible at this time).
            if not child._is_definite() \
                    and len(child.task_spec.outputs) > len(child.children):
                return True
        return False

    def _check_threshold_unstructured(self, my_task, force=False):
        # The default threshold is the number of inputs.
        threshold = valueof(my_task, self.threshold)
        if threshold is None:
            threshold = len(self.inputs)

        # Look at the tree to find all places where this task is used.
        tasks = []
        for input in self.inputs:
            tasks += my_task.workflow.task_mapping[my_task.thread_id][input]

        # Look up which tasks have already completed.
        waiting_tasks = []
        completed = 0
        for task in tasks:
            if task.parent is None or task._has_state(TaskState.COMPLETED):
                completed += 1
            else:
                waiting_tasks.append(task)

        # If the threshold was reached, get ready to fire.
        return force or completed >= threshold, waiting_tasks

    def _check_threshold_structured(self, my_task, force=False):
        # Retrieve a list of all activated tasks from the associated
        # task that did the conditional parallel split.
        split_task = my_task._find_ancestor_from_name(self.split_task)
        if split_task is None:
            msg = 'Join with %s, which was not reached' % self.split_task
            raise WorkflowException(self, msg)
        tasks = split_task.task_spec._get_activated_tasks(split_task, my_task)

        # The default threshold is the number of branches that were started.
        threshold = valueof(my_task, self.threshold)
        if threshold is None:
            threshold = len(tasks)

        # Look up which tasks have already completed.
        waiting_tasks = []
        completed = 0
        for task in tasks:
            # Refresh path prediction.
            task.task_spec._predict(task)

            if not self._branch_may_merge_at(task):
                completed += 1
            elif self._branch_is_complete(task):
                completed += 1
            else:
                waiting_tasks.append(task)

        # If the threshold was reached, get ready to fire.
        return force or completed >= threshold, waiting_tasks

    def _start(self, my_task, force=False):
        """
        Checks whether the preconditions for going to READY state are met.
        Returns True if the threshold was reached, False otherwise.
        Also returns the list of tasks that yet need to be completed.
        """
        # If the threshold was already reached, there is nothing else to do.
        if my_task._has_state(TaskState.COMPLETED):
            return True, None
        if my_task._has_state(TaskState.READY):
            return True, None

        # Check whether we may fire.
        if self.split_task is None:
            return self._check_threshold_unstructured(my_task, force)
        return self._check_threshold_structured(my_task, force)

    def _update_hook(self, my_task):
        # Check whether enough incoming branches have completed.
        may_fire, waiting_tasks = self._start(my_task)
        if not may_fire:
            my_task._set_state(TaskState.WAITING)
            return

        # If this is a cancelling join, cancel all incoming branches,
        # except for the one that just completed.
        if self.cancel_remaining:
            for task in waiting_tasks:
                task.cancel()

        # We do NOT set the task state to COMPLETED, because in
        # case all other incoming tasks get cancelled (or never reach
        # the Join for other reasons, such as reaching a stub branch),
        # we need to revisit it.
        my_task._ready()

        # Update the state of our child objects.
        self._do_join(my_task)

    def _do_join(self, my_task):
        # One Join spec may have multiple corresponding Task objects::
        #
        #     - Due to the MultiInstance pattern.
        #     - Due to the ThreadSplit pattern.
        #
        # When using the MultiInstance pattern, we want to join across
        # the resulting task instances. When using the ThreadSplit
        # pattern, we only join within the same thread. (Both patterns
        # may also be mixed.)
        #
        # We are looking for all task instances that must be joined.
        # We limit our search by starting at the split point.
        if self.split_task:
            split_task = my_task.workflow.get_task_spec_from_name(
                self.split_task)
            split_task = my_task._find_ancestor(split_task)
        else:
            split_task = my_task.workflow.task_tree

        # Identify all corresponding task instances within the thread.
        # Also remember which of those instances was most recently changed,
        # because we are making this one the instance that will
        # continue the thread of control. In other words, we will continue
        # to build the task tree underneath the most recently changed task.
        last_changed = None
        thread_tasks = []
        for task in split_task._find_any(self):
            # Ignore tasks from other threads.
            if task.thread_id != my_task.thread_id:
                continue
            # Ignore my outgoing branches.
            if self.split_task and task._is_descendant_of(my_task):
                continue

            # We have found a matching instance.
            thread_tasks.append(task)

            # Check whether the state of the instance was recently
            # changed.
            changed = task.parent.last_state_change
            if last_changed is None \
                    or changed > last_changed.parent.last_state_change:
                last_changed = task

        # Mark the identified task instances as COMPLETED. The exception
        # is the most recently changed task, for which we assume READY.
        # By setting the state to READY only, we allow for calling
        # :class:`Task.complete()`, which leads to the task tree being
        # (re)built underneath the node.
        for task in thread_tasks:
            if task == last_changed:
                self.entered_event.emit(my_task.workflow, my_task)
                task._ready()
            else:
                task._set_state(TaskState.COMPLETED)
                task._drop_children()



    def _on_trigger(self, my_task):
        """
        May be called to fire the Join before the incoming branches are
        completed.
        """
        for task in my_task.workflow.task_tree._find_any(self):
            if task.thread_id != my_task.thread_id:
                continue
            self._do_join(task)

    def serialize(self, serializer):
        return serializer.serialize_join(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_join(wf_spec, s_state)
