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
from SpiffWorkflow.TaskInstance import TaskInstance
from SpiffWorkflow.Exception    import WorkflowException
from Task                       import Task

class AcquireMutex(Task):
    """
    This class implements a task that acquires a mutex (lock), protecting
    a section of the workflow from being accessed by other sections.
    If more than one input is connected, the task performs an implicit
    multi merge.
    If more than one output is connected, the task performs an implicit
    parallel split.
    """

    def __init__(self, parent, name, mutex, **kwargs):
        """
        Constructor.

        parent -- a reference to the parent (Task)
        name -- a name for the task (string)
        mutex -- the mutex that should be acquired
        """
        assert mutex is not None
        Task.__init__(self, parent, name, **kwargs)
        self.mutex = mutex


    def _update_state_hook(self, instance):
        mutex = instance.job.get_mutex(self.mutex)
        if mutex.testandset():
            return True
        instance._set_state(TaskInstance.WAITING)
        return False


    def _on_complete_hook(self, task_instance):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.

        task_instance -- the task_instance in which this method is executed
        """
        return Task._on_complete_hook(self, task_instance)
