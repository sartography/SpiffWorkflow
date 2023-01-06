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

from ...operators import Operator
from ...specs.base import TaskSpec


class _BpmnCondition(Operator):

    def __init__(self, *args):
        if len(args) > 1:
            raise TypeError("Too many arguments")
        super(_BpmnCondition, self).__init__(*args)

    def _matches(self, task):
        return task.workflow.script_engine.evaluate(task, self.args[0])



class BpmnSpecMixin(TaskSpec):
    """
    All BPMN spec classes should mix this superclass in. It adds a number of
    methods that are BPMN specific to the TaskSpec.
    """

    def __init__(self, wf_spec, name, lane=None, position=None, **kwargs):
        """
        Constructor.

        :param lane: Indicates the name of the lane that this task belongs to
        (optional).
        """
        super(BpmnSpecMixin, self).__init__(wf_spec, name, **kwargs)
        self.lane = lane
        self.position = position or {'x': 0, 'y': 0}
        self.loopTask = False
        self.documentation = None
        self.data_input_associations = []
        self.data_output_associations = []

    @property
    def spec_type(self):
        return 'BPMN Task'

    def is_loop_task(self):
        """
        Returns true if this task is a BPMN looping task
        """
        return self.loopTask

    def connect_outgoing_if(self, condition, taskspec):
        """
        Connect this task spec to the indicated child, if the condition
        evaluates to true. This should only be called if the task has a
        connect_if method (e.g. ExclusiveGateway).
        """
        self.connect_if(_BpmnCondition(condition), taskspec)

    def _on_ready_hook(self, my_task):
        super()._on_ready_hook(my_task)
        for obj in self.data_input_associations:
            obj.get(my_task)

    def _on_complete_hook(self, my_task):

        for obj in self.data_output_associations:
            obj.set(my_task)

        for obj in self.data_input_associations:
            # Remove the any copied input variables that might not have already been removed
            my_task.data.pop(obj.name, None)

        super(BpmnSpecMixin, self)._on_complete_hook(my_task)
        if isinstance(my_task.parent.task_spec, BpmnSpecMixin):
            my_task.parent.task_spec._child_complete_hook(my_task)

    def _child_complete_hook(self, child_task):
        pass
