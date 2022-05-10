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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,MA  02110-1301  USA
from ..task import TaskState
from .base import TaskSpec


class AcquireMutex(TaskSpec):

    """
    This class implements a task that acquires a mutex (lock), protecting
    a section of the workflow from being accessed by other sections.
    If more than one input is connected, the task performs an implicit
    multi merge.
    If more than one output is connected, the task performs an implicit
    parallel split.
    """

    def __init__(self, wf_spec, name, mutex, **kwargs):
        """
        Constructor.

        :type  wf_spec: WorkflowSpec
        :param wf_spec: A reference to the workflow specification.
        :type  name: str
        :param name: The name of the task spec.
        :type  mutex: str
        :param mutex: The name of the mutex that should be acquired.
        :type  kwargs: dict
        :param kwargs: See :class:`SpiffWorkflow.specs.TaskSpec`.
        """
        assert mutex is not None
        TaskSpec.__init__(self, wf_spec, name, **kwargs)
        self.mutex = mutex

    def _update_hook(self, my_task):
        mutex = my_task.workflow._get_mutex(self.mutex)
        if mutex.testandset():
            self.entered_event.emit(my_task.workflow, my_task)
            my_task._ready()
            return
        my_task._set_state(TaskState.WAITING)

    def serialize(self, serializer):
        return serializer.serialize_acquire_mutex(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_acquire_mutex(wf_spec, s_state)
