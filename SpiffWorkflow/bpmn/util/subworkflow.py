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

from SpiffWorkflow import Workflow
from SpiffWorkflow.exceptions import TaskNotFoundException
from .task import BpmnTaskIterator

class BpmnBaseWorkflow(Workflow):

    def __init__(self, spec, **kwargs):
        super().__init__(spec, **kwargs)
        if len(spec.data_objects) > 0:
            self.data['data_objects'] = {}
    
    @property
    def data_objects(self):
        return self.data.get('data_objects', {})

    def get_tasks_iterator(self, first_task=None, **kwargs):
        return BpmnTaskIterator(first_task or self.task_tree, **kwargs)


class BpmnSubWorkflow(BpmnBaseWorkflow):

    def __init__(self, spec, parent_task_id, top_workflow, **kwargs):
        super().__init__(spec, **kwargs)
        self.parent_task_id = parent_task_id
        self.top_workflow = top_workflow
        self.correlations = {}
        self.depth = self._calculate_depth()

    @property
    def script_engine(self):
        return self.top_workflow.script_engine

    @property
    def parent_workflow(self):
        task = self.top_workflow.get_task_from_id(self.parent_task_id)
        return task.workflow

    def _calculate_depth(self):
        current, depth = self, 0
        while current.parent_workflow is not None:
            depth += 1
            current = current.parent_workflow
        return depth

    def get_task_from_id(self, task_id):
        try:
            return super().get_task_from_id(task_id)
        except TaskNotFoundException as exc:
            pass