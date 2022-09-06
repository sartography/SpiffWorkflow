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

from .Join import Join
from ..util.deep_merge import DeepMerge


class Merge(Join):

    """Same as Join, but merges all input data instead of just parents'

    Note: data fields that have conflicting names will be overwritten"""

    def _do_join(self, my_task):
        # Merge all inputs (in order)
        for input_spec in self.inputs:
            tasks = [task for task in my_task.workflow.task_tree
                     if task.task_spec is input_spec]
            for task in tasks:
                DeepMerge.merge(my_task.data, task.data)
        return super(Merge, self)._do_join(my_task)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_merge(wf_spec, s_state)
