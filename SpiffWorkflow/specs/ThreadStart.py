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
from SpiffWorkflow.Task import Task
from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.specs.TaskSpec import TaskSpec

class ThreadStart(TaskSpec):
    """
    This class implements the task the is placed at the beginning
    of each thread. It is NOT supposed to be used by in the API, it is
    used internally only (by the ThreadSplit task).
    The task has no inputs and at least one output.
    If more than one output is connected, the task does an implicit
    parallel split.
    """

    def __init__(self, parent, **kwargs):
        """
        Constructor. The name of this task is *always* 'ThreadStart'.
        
        :type  parent: TaskSpec
        :param parent: A reference to the parent task spec.
        :type  kwargs: dict
        :param kwargs: See L{SpiffWorkflow.specs.TaskSpec}.
        """
        TaskSpec.__init__(self, parent, 'ThreadStart', **kwargs)
        self.internal = True

    def _on_complete_hook(self, my_task):
        my_task._assign_new_thread_id()
        TaskSpec._on_complete_hook(self, my_task)

    def serialize(self, serializer):
        return serializer._serialize_thread_start(self)
