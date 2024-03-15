# Copyright (C) 2007 Samuel Abels, 2023 Sartography
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

from SpiffWorkflow.task import Task
from SpiffWorkflow.util.task import TaskState, TaskIterator
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
        for task in TaskIterator(my_task, state=TaskState.NOT_FINISHED_MASK):
            # If the current task is a child of myself, ignore it.
            if skip is not None and task.is_descendant_of(skip):
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
            if child.has_state(TaskState.PREDICTED_MASK) and len(child.task_spec.outputs) > len(child.children):
                return True
        return False

    def _get_split_task(self, my_task):
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
            split_task = my_task.find_ancestor(self.split_task)
        else:
            split_task = my_task.workflow.task_tree
        return split_task

    def _check_threshold_unstructured(self, my_task):
        # The default threshold is the number of inputs.
        threshold = valueof(my_task, self.threshold)
        if threshold is None:
            threshold = len(self.inputs)

        # Find all places where this task spec is used and check whether enough inputs have completed to meet the threshold
        # Omit building the list of waiting tasks unless they need to be cancelled if the threshold is met
        waiting_tasks = []
        completed = 0
        spec_names = [ts.name for ts in self.inputs]
        for task in TaskIterator(my_task.workflow.task_tree, end_at_spec=self.name):
            if not task.task_spec.name in spec_names:
                continue
            if task.parent is None or task.has_state(TaskState.COMPLETED):
                completed += 1
            elif not task.has_state(TaskState.FINISHED_MASK) and self.cancel_remaining:
                waiting_tasks.append(task)
            if completed >= threshold:
                may_fire = True
                break
        else:
            may_fire = False

        # If the threshold was reached, get ready to fire.
        return may_fire, waiting_tasks

    def _check_threshold_structured(self, my_task):
        # Retrieve a list of all activated tasks from the associated task that did the conditional parallel split.
        split_task = my_task.find_ancestor(self.split_task)
        if split_task is None:
            raise WorkflowException(f'Join with {self.split_task} which was not reached', task_spec=self)
        tasks = split_task.task_spec._get_activated_tasks(split_task, my_task)

        # The default threshold is the number of branches that were started.
        threshold = valueof(my_task, self.threshold)
        if threshold is None:
            threshold = len(tasks)

        # Look up which tasks have already completed.
        waiting_tasks = []
        completed = 0
        for task in tasks:
            if not self._branch_may_merge_at(task):
                completed += 1
            elif self._branch_is_complete(task):
                completed += 1
            else:
                waiting_tasks.append(task)

        # If the threshold was reached, get ready to fire.
        return completed >= threshold, waiting_tasks

    def _update_hook(self, my_task):

        # Check whether enough incoming branches have completed.
        my_task._inherit_data()
        if my_task.has_state(TaskState.FINISHED_MASK):
            may_fire, waiting_tasks = False, []
        elif self.split_task is None:
            may_fire, waiting_tasks = self._check_threshold_unstructured(my_task)
        else:
            may_fire, waiting_tasks = self._check_threshold_structured(my_task)

        if may_fire:
            # If this is a cancelling join, cancel all incoming branches except for the one that just completed.
            if self.cancel_remaining:
                for task in waiting_tasks:
                    task.cancel()
            # Update the state of our child objects.
            self._do_join(my_task)
        elif not my_task.has_state(TaskState.FINISHED_MASK):
            my_task._set_state(TaskState.WAITING)

        return may_fire

    def _find_tasks(self, my_task):

        split_task = self._get_split_task(my_task) or my_task.workflow.task_tree
        # Identify all corresponding task instances within the thread.
        thread_tasks = []
        for task in TaskIterator(split_task, spec_name=self.name, end_at_spec=self.name):
            # Ignore tasks from other threads.
            if task.thread_id != my_task.thread_id:
                continue
            # Ignore my outgoing branches.
            if self.split_task and task.is_descendant_of(my_task):
                continue
            # We have found a matching instance.
            thread_tasks.append(task)
        return thread_tasks

    def _do_join(self, my_task):

        # Execution will continue from this task; mark others as cancelled
        for task in self._find_tasks(my_task):
            if task != my_task:
                task._set_state(TaskState.CANCELLED)
                task._drop_children()

    def _on_trigger(self, my_task):
        """
        May be called to fire the Join before the incoming branches are
        completed.
        """
        tasks = sorted(self._find_tasks(my_task), key=lambda t: t.last_state_change)
        for task in tasks[:-1]:
            task._set_state(TaskState.CANCELLED)
            task._drop_children()
        tasks[-1]._ready()

    def serialize(self, serializer):
        return serializer.serialize_join(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_join(wf_spec, s_state)
