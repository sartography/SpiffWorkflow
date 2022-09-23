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
from ...exceptions import WorkflowException

from .BpmnSpecMixin import BpmnSpecMixin
from ...specs import TaskSpec
from ...specs.ExclusiveChoice import ExclusiveChoice


class ExclusiveGateway(ExclusiveChoice, BpmnSpecMixin):

    """
    Task Spec for a bpmn:exclusiveGateway node.
    """

    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        # This has been overridden to allow a single default flow out (without a
        # condition) - useful for the converging type
        TaskSpec.test(self)
#        if len(self.cond_task_specs) < 1:
#            raise WorkflowException(self, 'At least one output required.')
        for condition, name in self.cond_task_specs:
            if name is None:
                raise WorkflowException(self, 'Condition with no task spec.')
            task_spec = self._wf_spec.get_task_spec_from_name(name)
            if task_spec is None:
                msg = 'Condition leads to non-existent task ' + repr(name)
                raise WorkflowException(self, msg)
            if condition is None:
                continue

    @property
    def spec_type(self):
        return 'Exclusive Gateway'

    def serialize(self, serializer):
        return serializer.serialize_exclusive_gateway(self)


    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_exclusive_gateway(wf_spec, s_state)
