# -*- coding: utf-8 -*-

# Copyright (C) 2007 Samuel Abels
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
from ..exceptions import WorkflowException
from .base import TaskSpec


class Cancel(TaskSpec):

    """
    This class cancels a complete workflow.
    If more than one input is connected, the task performs an implicit
    multi merge.
    If more than one output is connected, the task performs an implicit
    parallel split.
    """

    def __init__(self, wf_spec, name, success=False, **kwargs):
        """
        Constructor.

        :type  wf_spec: WorkflowSpec
        :param wf_spec: A reference to the workflow specification.
        :type  name: str
        :param name: The name of the task spec.
        :type  success: bool
        :param success: Whether to cancel successfully or unsuccessfully.
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.TaskSpec`.
        """
        TaskSpec.__init__(self, wf_spec, name, **kwargs)
        self.cancel_successfully = success

    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        TaskSpec.test(self)
        if len(self.outputs) > 0:
            raise WorkflowException(self, 'Cancel with an output.')

    def _on_complete_hook(self, my_task):
        my_task.workflow.cancel(self.cancel_successfully)
        TaskSpec._on_complete_hook(self, my_task)

    def serialize(self, serializer):
        return serializer.serialize_cancel(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_cancel(wf_spec, s_state)
