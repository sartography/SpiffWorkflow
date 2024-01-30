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

from SpiffWorkflow.util.task import TaskFilter, TaskIterator
from SpiffWorkflow.bpmn.specs.mixins.events.event_types import CatchingEvent

class BpmnTaskFilter(TaskFilter):

    def __init__(self, catches_event=None, lane=None, **kwargs):
        super().__init__(**kwargs)
        self.catches_event = catches_event
        self.lane = lane

    def matches(self, task):

        def _catches_event(task):
            return isinstance(task.task_spec, CatchingEvent) and task.task_spec.catches(task, self.catches_event)

        return all([
            super().matches(task),
            self.catches_event is None or _catches_event(task),
            self.lane is None or task.task_spec.lane == self.lane,
        ])


class BpmnTaskIterator(TaskIterator):

    def __init__(self, task, end_at_spec=None, max_depth=1000, depth_first=True, task_filter=None, **kwargs):

        task_filter = task_filter or BpmnTaskFilter(**kwargs)
        super().__init__(task, end_at_spec, max_depth, depth_first, task_filter)

    def _next(self):

        if len(self.task_list) == 0:
            raise StopIteration()

        task = self.task_list.pop(0)
        subprocess = task.workflow.top_workflow.subprocesses.get(task.id)

        if task.task_spec.name == self.end_at_spec:
            self.task_list = []
        elif all([
            len(task._children) > 0 or subprocess is not None,
            task.state >= self.min_state or subprocess is not None,
            self.depth < self.max_depth,
        ]):
            if subprocess is None:
                next_tasks = task.children
            elif self.depth_first:
                next_tasks = [subprocess.task_tree] + task.children
            else:
                next_tasks = task.children + [subprocess.task_tree]

            if self.depth_first:
                self.task_list = next_tasks + self.task_list
            else:
                self.task_list.extend(next_tasks)
            self._update_depth(task)

        elif self.depth_first and len(self.task_list) > 0:
            self._handle_leaf_depth(task)

        return task