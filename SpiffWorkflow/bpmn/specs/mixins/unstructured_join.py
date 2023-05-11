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

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.specs.Join import Join


class UnstructuredJoin(Join):
    """
    A helper subclass of Join that makes it work in a slightly friendlier way
    for the BPMN style threading
    """
    def _get_inputs_with_tokens(self, my_task):
        # Look at the tree to find all places where this task is used.
        tasks = [ t for t in my_task.workflow.get_tasks_from_spec_name(self.name) if t.workflow == my_task.workflow ]

        # Look up which tasks have parents completed.
        waiting_tasks = []
        completed_inputs = set()
        for task in tasks:
            if task.parent.state == TaskState.COMPLETED:
                completed_inputs.add(task.parent.task_spec)
            # Ignore predicted tasks; we don't care about anything not definite
            elif task.parent._has_state(TaskState.READY | TaskState.FUTURE | TaskState.WAITING):
                waiting_tasks.append(task.parent)

        return completed_inputs, waiting_tasks

    def _do_join(self, my_task):
        split_task = self._get_split_task(my_task)

        # Identify all corresponding task instances within the thread.
        # Also remember which of those instances was most recently changed,
        # because we are making this one the instance that will
        # continue the thread of control. In other words, we will continue
        # to build the task tree underneath the most recently changed task.
        last_changed = None
        thread_tasks = []
        for task in split_task._find_any(self):
            if task.thread_id != my_task.thread_id:
                # Ignore tasks from other threads.  (Do we need this condition?)
                continue
            if not task.parent._is_finished():
                # For an inclusive join, this can happen - it's a future join
                continue
            if my_task._is_descendant_of(task):
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
