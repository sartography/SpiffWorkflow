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
from MultiChoice import MultiChoice

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
        
        @type  parent: TaskSpec
        @param parent: A reference to the parent task spec.
        @type  name: str
        @param name: The name of the task spec.
        @type  kwargs: dict
        @param kwargs: See L{SpiffWorkflow.specs.TaskSpec}.
        """
        super(ExclusiveChoice, self).__init__(parent, name, **kwargs)
        self.default_task_spec = None


    def connect(self, task_spec):
        """
        Connects the task spec that is executed if no other condition
        matches.

        @type  task_spec: TaskSpec
        @param task_spec: The following task spec.
        """
        assert self.default_task_spec is None
        self.outputs.append(task_spec)
        self.default_task_spec = task_spec.name
        task_spec._connect_notify(self)


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        MultiChoice.test(self)
        if self.default_task_spec is None:
            raise WorkflowException(self, 'A default output is required.')


    def _predict_hook(self, my_task):
        my_task._update_children(self.outputs, Task.MAYBE)
        spec = self._parent.get_task_spec_from_name(self.default_task_spec)
        my_task._set_likely_task(spec)


    def _on_complete_hook(self, my_task):
        # Find the first matching condition.
        output = self._parent.get_task_spec_from_name(self.default_task_spec)
        for condition, spec_name in self.cond_task_specs:
            if condition is None or condition._matches(my_task):
                output = self._parent.get_task_spec_from_name(spec_name)
                break

        my_task._update_children(output)
        return True

    def serialize(self, serializer):
        return serializer._serialize_exclusive_choice(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer._deserialize_exclusive_choice(wf_spec, s_state)
