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
import re
from SpiffWorkflow.Task      import Task
from SpiffWorkflow.Exception import WorkflowException
from MultiChoice             import MultiChoice

class ExclusiveChoice(MultiChoice):
    """
    This class represents an exclusive choice (an if condition) task
    where precisely one outgoing task is selected. If none of the
    given conditions matches, a default task is selected.
    It has one or more inputs and two or more outputs.
    """
    def __init__(self, parent, name, **kwargs):
        """
        Constructor.
        
        parent -- a reference to the parent (TaskSpec)
        name -- a name for the pattern (string)
        """
        MultiChoice.__init__(self, parent, name, **kwargs)
        self.default_task = None


    def connect(self, taskspec):
        """
        Connects the task that is executed if no other condition matches.

        taskspec -- the following task
        """
        assert self.default_task is None
        self.outputs.append(taskspec)
        self.default_task = taskspec
        taskspec._connect_notify(self)


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        MultiChoice.test(self)
        if self.default_task is None:
            raise WorkflowException(self, 'A default output is required.')


    def _predict_hook(self, my_task):
        my_task._update_children(self.outputs, Task.MAYBE)
        my_task._set_likely_task(self.default_task)


    def _on_complete_hook(self, my_task):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        # Find the first matching condition.
        output = self.default_task
        for condition, taskspec in self.cond_taskspecs:
            if condition is None or condition._matches(my_task):
                output = taskspec
                break

        my_task._update_children(output)
        return True
