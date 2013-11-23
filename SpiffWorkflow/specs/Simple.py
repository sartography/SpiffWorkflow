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
from SpiffWorkflow.specs.TaskSpec import TaskSpec


class Simple(TaskSpec):
    """
    This class implements a task with one or more inputs and
    any number of outputs.
    If more than one input is connected, the task performs an implicit
    multi merge.
    If more than one output is connected, the task performs an implicit
    parallel split.
    """
    def serialize(self, serializer):
        return serializer._serialize_simple(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer._deserialize_simple(wf_spec, s_state)
