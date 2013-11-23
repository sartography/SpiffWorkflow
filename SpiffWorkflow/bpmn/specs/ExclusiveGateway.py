# -*- coding: utf-8 -*-
from __future__ import division
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
from SpiffWorkflow.exceptions import WorkflowException

from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.TaskSpec import TaskSpec
from SpiffWorkflow.specs.ExclusiveChoice import ExclusiveChoice

class ExclusiveGateway(ExclusiveChoice, BpmnSpecMixin):
    """
    Task Spec for a bpmn:exclusiveGateway node.
    """
    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        #This has been overidden to allow a single default flow out (without a condition) - useful for
        #the converging type
        TaskSpec.test(self)
#        if len(self.cond_task_specs) < 1:
#            raise WorkflowException(self, 'At least one output required.')
        for condition, name in self.cond_task_specs:
            if name is None:
                raise WorkflowException(self, 'Condition with no task spec.')
            task_spec = self._parent.get_task_spec_from_name(name)
            if task_spec is None:
                msg = 'Condition leads to non-existent task ' + repr(name)
                raise WorkflowException(self, msg)
            if condition is None:
                continue
        if self.default_task_spec is None:
            raise WorkflowException(self, 'A default output is required.')