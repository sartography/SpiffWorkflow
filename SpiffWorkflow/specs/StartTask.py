# -*- coding: utf-8 -*-
from __future__ import division
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.specs.TaskSpec import TaskSpec


class StartTask(TaskSpec):
    """
    This class implements the task the is placed at the beginning
    of each workflow. The task has no inputs and at least one output.
    If more than one output is connected, the task does an implicit
    parallel split.
    """

    def __init__(self, parent, **kwargs):
        """
        Constructor. The name of this task is *always* 'Start'.

        :type  parent: TaskSpec
        :param parent: A reference to the parent task spec.
        :type  kwargs: dict
        :param kwargs: See L{SpiffWorkflow.specs.TaskSpec}.
        """
        TaskSpec.__init__(self, parent, 'Start', **kwargs)

    def _connect_notify(self, task_spec):
        """
        Called by the previous task to let us know that it exists.
        """
        raise WorkflowException(self, 'StartTask can not have any inputs.')

    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        if len(self.inputs) != 0:
            raise WorkflowException(self, 'StartTask with an input.')
        elif len(self.outputs) < 1:
            raise WorkflowException(self, 'No output task connected.')

    def serialize(self, serializer):
        return serializer._serialize_start_task(self)

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state):
        return serializer._deserialize_start_task(wf_spec, s_state)
