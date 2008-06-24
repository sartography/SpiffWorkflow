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
from SpiffWorkflow.TaskInstance import TaskInstance
from SpiffWorkflow.Exception    import WorkflowException
from SpiffWorkflow.Operators    import valueof
from TaskSpec                   import TaskSpec

class MultiInstance(TaskSpec):
    """
    When executed, this task performs a split on the current instance.
    The number of outgoing instances depends on the runtime value of a
    specified attribute.
    If more than one input is connected, the task performs an implicit
    multi merge.

    This task has one or more inputs and may have any number of outputs.
    """

    def __init__(self, parent, name, **kwargs):
        """
        Constructor.
        
        parent -- a reference to the parent (TaskSpec)
        name -- a name for the pattern (string)
        kwargs -- must contain one of the following:
                    times -- the number of instances to create.
        """
        assert kwargs.has_key('times')
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.times = kwargs.get('times', None)


    def _find_my_instance(self, instance):
        for node in instance.job.task_tree:
            if node.thread_id != instance.thread_id:
                continue
            if node.task == self:
                return node
        return None


    def _on_trigger(self, instance):
        """
        May be called after execute() was already completed to create an
        additional outbound instance.
        """
        # Find a TaskInstance for this task.
        my_instance = self._find_my_instance(instance)
        for output in self.outputs:
            if my_instance._has_state(TaskInstance.COMPLETED):
                state = TaskInstance.READY | TaskInstance.TRIGGERED
            else:
                state = TaskInstance.FUTURE | TaskInstance.TRIGGERED
            node = my_instance._add_child(output, state)
            output._predict(node)


    def _get_predicted_outputs(self, instance):
        split_n = instance._get_internal_attribute('splits', 1)

        # Predict the outputs.
        outputs = []
        for i in range(split_n):
            outputs += self.outputs
        return outputs


    def _predict_hook(self, instance):
        split_n = valueof(instance, self.times)
        if split_n is None:
            return
        instance._set_internal_attribute(splits = split_n)

        # Create the outgoing nodes.
        outputs = []
        for i in range(split_n):
            outputs += self.outputs

        if instance._has_state(TaskInstance.LIKELY):
            child_state = TaskInstance.LIKELY
        else:
            child_state = TaskInstance.FUTURE
        instance._update_children(outputs, child_state)


    def _on_complete_hook(self, instance):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        outputs = self._get_predicted_outputs(instance)
        instance._update_children(outputs)
        return True
