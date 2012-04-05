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
from SpiffWorkflow.Task import Task
from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.specs.TaskSpec import TaskSpec

class Wait(TaskSpec):
    """
    This class demonstrates a simple way to have a task wait for an external
    resource. It basically counts the number of times it gets called and
    completes after hitting the specified threshold.
    """

    def __init__(self, parent, name, count, **kwargs):
        """
        Constructor.

        @type  parent: TaskSpec
        @param parent: A reference to the parent task spec.
        @type  name: str
        @param name: The name of the task spec.
        @type  count: int
        @param count: How many times to respond with Waiting before Ready.
        @type  kwargs: dict
        @param kwargs: See L{SpiffWorkflow.specs.TaskSpec}.
        """
        assert parent  is not None
        assert name    is not None
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.count = count
        self.counter = 0    # We use this to implement the waiting

    def try_fire(self):
        """Returns False when successfully fired, True otherwise"""
        if self.counter == self.count:
            return True
        self.counter += 1
        return False

    def _update_state_hook(self, my_task):
        if not self.try_fire():
            my_task.state = Task.WAITING
            result = False
        else:
            result = super(Wait, self)._update_state_hook(my_task)
        return result
