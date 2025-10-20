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
from copy import deepcopy

from SpiffWorkflow.util.deep_merge import DeepMerge
from SpiffWorkflow.util.task import TaskState, TaskIterator
from SpiffWorkflow.specs.Join import Join

class UnstructuredJoin(Join):
    """
    A helper subclass of Join that makes it work in a slightly friendlier way
    for the BPMN style threading
    """
    def _update_hook(self, my_task):

        may_fire = self._check_threshold_unstructured(my_task)
        other_tasks = [t for t in my_task.workflow.tasks.values()
                if t.task_spec == self and t != my_task and t.state is TaskState.WAITING]
        for task in other_tasks:
            # By cancelling other waiting tasks immediately, we can prevent them from being updated repeeatedly and pointlessly
            task.cancel()
        if not may_fire:
            # Only the most recent instance of the spec needs to wait.
            my_task._set_state(TaskState.WAITING)
        else:
            # Only copy the data to the task that will proceed
            my_task._inherit_data()
        return may_fire

    def _run_hook(self, my_task):
        other_tasks = filter(
            lambda t: t.task_spec == self and t.has_state(TaskState.FINISHED_MASK) and not my_task.is_descendant_of(t),
            my_task.workflow.tasks.values()
        )
        for task in sorted(other_tasks, key=lambda t: t.last_state_change):
            # By inheriting directly from parent tasks, we can avoid copying previouly merged data

            DeepMerge.merge(my_task.data, task.parent.data)
            # This condition only applies when a workflow is reset inside a parallel branch.
            # If reset to a branch that was originally cancelled, all the descendants of the previously completed branch will still
            # appear in the tree, potentially corrupting the structure and data.
            if task.has_state(TaskState.COMPLETED):
                task._drop_children(force=True)

        # My task is not finished, so won't be included above.
        my_task._inherit_data()
        return True
