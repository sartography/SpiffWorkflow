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
from SpiffWorkflow.Exception import WorkflowException
from SpiffWorkflow.specs.TaskSpec import TaskSpec
from SpiffWorkflow.operators import valueof

class Join(TaskSpec):
    """
    A task for synchronizing branches that were previously split using a
    conditional task, such as MultiChoice. It has two or more incoming
    branches and one or more outputs.
    """

    def __init__(self,
                 parent,
                 name,
                 split_task = None,
                 threshold = None,
                 cancel = False,
                 **kwargs):
        """
        Constructor.
        
        @type  parent: L{SpiffWorkflow.specs.WorkflowSpec}
        @param parent: A reference to the parent (usually a workflow).
        @type  name: string
        @param name: A name for the task.
        @type  split_task: str or None
        @param split_task: The name of the task spec that was previously
                           used to split the branch. If this is None,
                           the most recent branch split is merged.
        @type  threshold: int or L{SpiffWorkflow.operators.Attrib}
        @param threshold: Specifies how many incoming branches need to
                          complete before the task triggers. When the limit
                          is reached, the task fires but still expects all
                          other branches to complete.
                          You may also pass an attribute, in which case
                          the value is resolved at runtime.
        @type  cancel: bool
        @param cancel: When True, any remaining incoming branches are
                       cancelled as soon as the discriminator is activated.
        @type  kwargs: dict
        @param kwargs: See L{SpiffWorkflow.specs.TaskSpec}.
        """
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.split_task       = split_task
        self.threshold        = threshold
        self.cancel_remaining = cancel


    def _branch_is_complete(self, my_task):
        # Determine whether that branch is now completed by checking whether
        # it has any waiting items other than myself in it.
        skip  = None
        for task in Task.Iterator(my_task, my_task.NOT_FINISHED_MASK):
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
            if child._has_state(Task.TRIGGERED):
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


    def _fire(self, my_task, waiting_tasks):
        """
        Fire, and cancel remaining tasks, if so requested.
        """
        # If this is a cancelling join, cancel all incoming branches,
        # except for the one that just completed.
        if self.cancel_remaining:
            for task in waiting_tasks:
                task.cancel()


    def _try_fire_unstructured(self, my_task, force = False):
        # If the threshold was already reached, there is nothing else to do.
        if my_task._has_state(Task.COMPLETED):
            return False
        if my_task._has_state(Task.READY):
            return True

        # The default threshold is the number of inputs.
        threshold = valueof(my_task, self.threshold)
        if threshold is None:
            threshold = len(self.inputs)

        # Look at the tree to find all places where this task is used.
        tasks = []
        for input in self.inputs:
            for task in my_task.workflow.task_tree:
                if task.thread_id != my_task.thread_id:
                    continue
                if task.task_spec != input:
                    continue
                tasks.append(task)

        # Look up which tasks have already completed.
        waiting_tasks = []
        completed     = 0
        for task in tasks:
            if task.parent is None or task._has_state(Task.COMPLETED):
                completed += 1
            else:
                waiting_tasks.append(task)

        # If the threshold was reached, get ready to fire.
        if force or completed >= threshold:
            self._fire(my_task, waiting_tasks)
            return True

        # We do NOT set the task state to COMPLETED, because in
        # case all other incoming tasks get cancelled (or never reach
        # the Join for other reasons, such as reaching a stub branch), we
        # we need to revisit it.
        return False


    def _try_fire_structured(self, my_task, force = False):
        # If the threshold was already reached, there is nothing else to do.
        if my_task._has_state(Task.READY):
            return True
        if my_task._has_state(Task.COMPLETED):
            return False

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
        completed     = 0
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
        if force or completed >= threshold:
            self._fire(my_task, waiting_tasks)
            return True

        # We do NOT set the task state to COMPLETED, because in
        # case all other incoming tasks get cancelled (or never reach
        # the Join for other reasons, such as reaching a stub branch), we
        # need to revisit it.
        return False


    def try_fire(self, my_task, force = False):
        if self.split_task is None:
            return self._try_fire_unstructured(my_task, force)
        return self._try_fire_structured(my_task, force)


    def _do_join(self, my_task):
        if self.split_task:
            split_task = my_task.workflow.get_task_spec_from_name(self.split_task)
            split_task = my_task._find_ancestor(split_task)
        else:
            split_task = my_task.workflow.task_tree

        # Find the inbound task that was completed last.
        last_changed = None
        thread_tasks = []
        for task in split_task._find_any(self):
            if task.thread_id != my_task.thread_id:
                continue
            if self.split_task and task._is_descendant_of(my_task):
                continue
            changed = task.parent.last_state_change
            if last_changed is None \
              or changed > last_changed.parent.last_state_change:
                last_changed = task
            thread_tasks.append(task)

        # Mark all tasks in this thread that reference this task as 
        # completed, except for the first one, which should be READY.
        for task in thread_tasks:
            if task == last_changed:
                self.entered_event.emit(my_task.workflow, my_task)
                task._ready()
            else:
                task.state = Task.COMPLETED
                task._drop_children()
        return False


    def _on_trigger(self, my_task):
        """
        May be called to fire the Join before the incoming branches are
        completed.
        """
        for task in my_task.workflow.task_tree._find_any(self):
            if task.thread_id != my_task.thread_id:
                continue
            return self._do_join(task)


    def _update_state_hook(self, my_task):
        if not self.try_fire(my_task):
            my_task.state = Task.WAITING
            return False
        return self._do_join(my_task)


    def _on_complete_hook(self, my_task):
        return TaskSpec._on_complete_hook(self, my_task)
