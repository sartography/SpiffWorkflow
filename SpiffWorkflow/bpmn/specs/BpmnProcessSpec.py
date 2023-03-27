# -*- coding: utf-8 -*-
# Copyright (C) 2012 Matthew Hampton
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

from ...task import TaskState
from .UnstructuredJoin import UnstructuredJoin
from ...specs.Simple import Simple
from ...specs.WorkflowSpec import WorkflowSpec


class _EndJoin(UnstructuredJoin):

    def _check_threshold_unstructured(self, my_task, force=False):
        # Look at the tree to find all ready and waiting tasks (excluding
        # ourself). The EndJoin waits for everyone!
        waiting_tasks = []
        for task in my_task.workflow.get_tasks(TaskState.READY | TaskState.WAITING):
            if task.thread_id != my_task.thread_id:
                continue
            if task.task_spec == my_task.task_spec:
                continue

            is_mine = False
            w = task.workflow
            if w == my_task.workflow:
                is_mine = True
            while w and w.outer_workflow != w:
                w = w.outer_workflow
                if w == my_task.workflow:
                    is_mine = True
            if is_mine:
                waiting_tasks.append(task)

        return force or len(waiting_tasks) == 0, waiting_tasks

    def _run_hook(self, my_task):
        result = super(_EndJoin, self)._run_hook(my_task)
        my_task.workflow.data.update(my_task.data)
        return result


class BpmnProcessSpec(WorkflowSpec):
    """
    This class represents the specification of a BPMN process workflow. This
    specialises the standard Spiff WorkflowSpec class with a few extra methods
    and attributes.
    """

    def __init__(self, name=None, description=None, filename=None, svg=None):
        """
        Constructor.

        :param svg: This provides the SVG representation of the workflow as an
        LXML node. (optional)
        """
        super(BpmnProcessSpec, self).__init__(name=name, filename=filename)
        self.end = _EndJoin(self, '%s.EndJoin' % (self.name))
        self.end.connect(Simple(self, 'End'))
        self.svg = svg
        self.description = description
        self.io_specification = None
        self.data_objects = {}
        self.data_stores = {}
        self.correlation_keys = {}
