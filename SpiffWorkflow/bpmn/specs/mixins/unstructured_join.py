# Copyright (C) 2012 Matthew Hampton, 2023 Sartography
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

from SpiffWorkflow.util.task import TaskState, TaskIterator
from SpiffWorkflow.specs.Join import Join


class UnstructuredJoin(Join):
    """
    A helper subclass of Join that makes it work in a slightly friendlier way
    for the BPMN style threading
    """
    def _do_join(self, my_task):
        split_task = my_task.find_ancestor(self.split_task) or my_task.workflow.task_tree

        # Identify all corresponding task instances within the thread.
        # Also remember which of those instances was most recently changed,
        # because we are making this one the instance that will
        # continue the thread of control. In other words, we will continue
        # to build the task tree underneath the most recently changed task.
        last_changed = None
        thread_tasks = []
        for task in TaskIterator(split_task, spec_name=self.name):
            if not task.parent.has_state(TaskState.FINISHED_MASK):
                # For an inclusive join, this can happen - it's a future join
                continue
            if my_task.is_descendant_of(task):
                # Skip ancestors (otherwise the branch this task is on will get dropped)
                continue
            # We have found a matching instance.
            thread_tasks.append(task)

            # Check whether the state of the instance was recently changed.
            changed = task.parent.last_state_change
            if last_changed is None or changed > last_changed.parent.last_state_change:
                last_changed = task

        # Update data from all the same thread tasks.
        thread_tasks.sort(key=lambda t: t.parent.last_state_change)
        collected_data = {}
        for task in thread_tasks:
            collected_data.update(task.data)

        for task in thread_tasks:
            if task != last_changed:
                task._set_state(TaskState.CANCELLED)
                task._drop_children()
            else:
                task.data.update(collected_data)

    def _update_hook(self, my_task):

        # Check whether enough incoming branches have completed.
        my_task._inherit_data()
        may_fire = self._check_threshold_unstructured(my_task)
        if may_fire:
            self._do_join(my_task)
        elif not my_task.has_state(TaskState.FINISHED_MASK):
            my_task._set_state(TaskState.WAITING)
        return may_fire
