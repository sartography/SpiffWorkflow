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
    def _update_hook(self, my_task):

        my_task._inherit_data()
        may_fire = self._check_threshold_unstructured(my_task)
        other_tasks = [t for t in my_task.workflow.tasks.values() if t.task_spec == self and t != my_task and t.state is TaskState.WAITING]
        for task in other_tasks:
            my_task.data.update(task.data)
            task.cancel()
        if not may_fire:
            my_task._set_state(TaskState.WAITING)
        return may_fire
