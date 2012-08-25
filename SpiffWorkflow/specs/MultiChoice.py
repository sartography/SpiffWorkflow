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
from SpiffWorkflow.Task import Task
from SpiffWorkflow.exceptions import WorkflowException
from TaskSpec import TaskSpec

class MultiChoice(TaskSpec):
    """
    This class represents an if condition where multiple conditions may match
    at the same time, creating multiple outgoing branches.
    This task has one or more inputs, and one or more incoming branches.
    This task has one or more outputs.
    """

    def __init__(self, parent, name, **kwargs):
        """
        Constructor.
        
        @type  parent: TaskSpec
        @param parent: A reference to the parent task spec.
        @type  name: str
        @param name: The name of the task spec.
        @type  kwargs: dict
        @param kwargs: See L{SpiffWorkflow.specs.TaskSpec}.
        """
        super(MultiChoice, self).__init__(parent, name, **kwargs)
        self.cond_task_specs = []
        self.choice          = None

    def connect(self, task_spec):
        """
        Convenience wrapper around connect_if() where condition is set to None.
        """
        return self.connect_if(None, task_spec)

    def connect_if(self, condition, task_spec):
        """
        Connects a taskspec that is executed if the condition DOES match.
        
        condition -- a condition (Condition)
        taskspec -- the conditional task spec
        """
        assert task_spec is not None
        self.outputs.append(task_spec)
        self.cond_task_specs.append((condition, task_spec.name))
        task_spec._connect_notify(self)

    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        TaskSpec.test(self)
        if len(self.cond_task_specs) < 1:
            raise WorkflowException(self, 'At least one output required.')
        for condition, name in self.cond_task_specs:
            if name is None:
                raise WorkflowException(self, 'Condition with no task spec.')
            task_spec = self._parent.get_task_spec_from_name(name)
            if task_spec is None:
                msg = 'Condition leads to non-existent task ' + repr(name)
                raise WorkflowException(self, msg)
            if condition is None:
                continue

    def _on_trigger(self, my_task, choice):
        """
        Lets a caller narrow down the choice by using a Choose trigger.
        """
        self.choice = choice

    def _predict_hook(self, my_task):
        my_task._update_children(self.outputs, Task.MAYBE)

    def _on_complete_hook(self, my_task):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        # Find all matching conditions.
        outputs = []
        for condition, output in self.cond_task_specs:
            if condition is not None and not condition._matches(my_task):
                continue
            if self.choice is not None and output not in self.choice:
                continue
            outputs.append(self._parent.get_task_spec_from_name(output))

        my_task._update_children(outputs)
        return True

    def serialize(self, serializer):
        return serializer._serialize_multi_choice(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer._deserialize_multi_choice(wf_spec, s_state)
