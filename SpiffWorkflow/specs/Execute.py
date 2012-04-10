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
import subprocess

from SpiffWorkflow.Task import Task
from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.specs.TaskSpec import TaskSpec


class Execute(TaskSpec):
    """
    This class executes an external process, goes into WAITING until the
    process is complete, and returns the results of the execution.

    Usage:

    task = Execute(spec, 'Ping', args=["ping", "-t", "1", "127.0.0.1"])
        ... when workflow complete
    print workflow.get_task('Ping').results
    """

    def __init__(self, parent, name, args=None, **kwargs):
        """
        Constructor.

        @type  parent: TaskSpec
        @param parent: A reference to the parent task spec.
        @type  name: str
        @param name: The name of the task spec.
        @type  args: list
        @param args: args to pass to process (first arg is the command).
        @type  kwargs: dict
        @param kwargs: kwargs to pass-through to TaskSpec initializer.
        """
        assert parent  is not None
        assert name    is not None
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.args = args

    def _try_fire(self, my_task, force = False):
        """Returns False when successfully fired, True otherwise"""
        if (not hasattr(my_task, 'subprocess')) or my_task.subprocess is None:
            my_task.subprocess = subprocess.Popen(self.args,
                                               stderr=subprocess.STDOUT,
                                               stdout=subprocess.PIPE)

        if my_task.subprocess:
            my_task.subprocess.poll()
            if my_task.subprocess.returncode is None:
                # Still waiting
                return False
            else:
                results = my_task.subprocess.communicate()
                my_task.results = results
                return True
        return False

    def _update_state_hook(self, my_task):
        if not self._try_fire(my_task):
            my_task.state = Task.WAITING
            result = False
        else:
            result = super(Execute, self)._update_state_hook(my_task)
        return result

    def serialize(self, serializer):
        return serializer._serialize_execute(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        spec = serializer._deserialize_execute(wf_spec, s_state)
        return spec
