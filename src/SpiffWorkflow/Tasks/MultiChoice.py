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
from SpiffWorkflow.Operators    import *
from SpiffWorkflow.TaskInstance import TaskInstance
from SpiffWorkflow.Exception    import WorkflowException
from TaskSpec                   import TaskSpec

class MultiChoice(TaskSpec):
    """
    This class represents an if condition where multiple conditions may match
    at the same time, creating multiple instances.
    This task has one or more inputs, and one or more incoming branches.
    This task has one or more outputs.
    """

    def __init__(self, parent, name, **kwargs):
        """
        Constructor.
        
        parent -- a reference to the parent (TaskSpec)
        name -- a name for the pattern (string)
        """
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.cond_tasks = []
        self.choice     = None


    def connect(self, task):
        """
        Convenience wrapper around connect_if() where condition is set to None.
        """
        return self.connect_if(None, task)


    def connect_if(self, condition, task):
        """
        Connects a task that is executed if the condition DOES match.
        
        condition -- a condition (Condition)
        task -- the conditional task
        """
        assert task is not None
        self.outputs.append(task)
        self.cond_tasks.append((condition, task))
        task._connect_notify(self)


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        TaskSpec.test(self)
        if len(self.cond_tasks) < 1:
            raise WorkflowException(self, 'At least one output required.')
        for condition, task in self.cond_tasks:
            if task is None:
                raise WorkflowException(self, 'Condition with no task.')
            if condition is None:
                continue
            if condition is None:
                raise WorkflowException(self, 'Condition is None.')


    def _on_trigger(self, instance, choice):
        """
        Lets a caller narrow down the choice by using a Choose trigger.
        """
        self.choice = choice


    def _predict_hook(self, instance):
        instance._update_children(self.outputs, TaskInstance.MAYBE)


    def _on_complete_hook(self, instance):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        # Find all matching conditions.
        outputs = []
        for condition, output in self.cond_tasks:
            if condition is not None and not condition._matches(instance):
                continue
            if self.choice is not None and output.name not in self.choice:
                continue
            outputs.append(output)

        instance._update_children(outputs)
        return True
