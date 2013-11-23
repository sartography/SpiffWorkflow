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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
import logging

from SpiffWorkflow.specs.TaskSpec import TaskSpec

LOG = logging.getLogger(__name__)


class Transform(TaskSpec):
    """
    This class implements a task that transforms input/output data.
    """

    def __init__(self, parent, name, transforms=None, **kwargs):
        """
        Constructor.

        :type  parent: TaskSpec
        :param parent: A reference to the parent task spec.
        :type  name: str
        :param name: The name of the task spec.
        :type  transforms: list
        :param transforms: The commands that this task will execute to
                        transform data. The commands will be executed using the
                        python 'exec' function. Accessing inputs and outputs is
                        achieved by referencing the my_task.* and self.*
                        variables'
        :type  kwargs: dict
        :param kwargs: See L{SpiffWorkflow.specs.TaskSpec}.
        """
        assert parent  is not None
        assert name    is not None
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.transforms = transforms

    def _update_state_hook(self, my_task):
        if self.transforms:
            for transform in self.transforms:
                LOG.debug("Executing transform", extra=dict(data=transform))
                exec(transform)
        super(Transform, self)._update_state_hook(my_task)

    def serialize(self, serializer):
        s_state = serializer._serialize_simple(self)
        s_state['transforms'] = self.transforms
        return s_state

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state):
        spec = Transform(wf_spec, s_state['name'])
        serializer._deserialize_task_spec(wf_spec, s_state, spec=spec)
        spec.transforms = s_state['transforms']
        return spec
