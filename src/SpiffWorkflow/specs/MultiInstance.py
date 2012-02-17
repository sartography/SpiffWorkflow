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
from SpiffWorkflow.Exception import WorkflowException
from SpiffWorkflow.specs.TaskSpec import TaskSpec
from SpiffWorkflow.operators import valueof

class MultiInstance(TaskSpec):
    """
    When executed, this task performs a split on the current task.
    The number of outgoing tasks depends on the runtime value of a
    specified attribute.
    If more than one input is connected, the task performs an implicit
    multi merge.

    This task has one or more inputs and may have any number of outputs.
    """

    def __init__(self, parent, name, **kwargs):
        """
        Constructor.
        
        @type  parent: TaskSpec
        @param parent: A reference to the parent task spec.
        @type  name: str
        @param name: The name of the task spec.
        @type  times: int
        @param times: The number of tasks to create.
        @type  kwargs: dict
        @param kwargs: See L{SpiffWorkflow.specs.TaskSpec}.
        """
        assert kwargs.has_key('times')
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.times = kwargs.get('times', None)


    def _find_my_task(self, task):
        for thetask in task.workflow.task_tree:
            if thetask.thread_id != task.thread_id:
                continue
            if thetask.task_spec == self:
                return thetask
        return None


    def _on_trigger(self, task_spec):
        """
        May be called after execute() was already completed to create an
        additional outbound task.
        """
        # Find a Task for this TaskSpec.
        my_task = self._find_my_task(task_spec)
        for output in self.outputs:
            if my_task._has_state(Task.COMPLETED):
                state = Task.READY | Task.TRIGGERED
            else:
                state = Task.FUTURE | Task.TRIGGERED
            output._predict(my_task._add_child(output, state))


    def _get_predicted_outputs(self, my_task):
        split_n = my_task._get_internal_attribute('splits', 1)

        # Predict the outputs.
        outputs = []
        for i in range(split_n):
            outputs += self.outputs
        return outputs


    def _predict_hook(self, my_task):
        split_n = valueof(my_task, self.times)
        if split_n is None:
            return
        my_task._set_internal_attribute(splits = split_n)

        # Create the outgoing tasks.
        outputs = []
        for i in range(split_n):
            outputs += self.outputs

        if my_task._has_state(Task.LIKELY):
            child_state = Task.LIKELY
        else:
            child_state = Task.FUTURE
        my_task._update_children(outputs, child_state)


    def _on_complete_hook(self, my_task):
        outputs = self._get_predicted_outputs(my_task)
        my_task._update_children(outputs)
        return True
