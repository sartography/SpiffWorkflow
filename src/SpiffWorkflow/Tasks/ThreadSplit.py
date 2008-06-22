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
from Task                       import Task
from ThreadStart                import ThreadStart

class ThreadSplit(Task):
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
        
        parent -- a reference to the parent (Task)
        name -- a name for the pattern (string)
        kwargs -- must contain one of the following:
                    times -- the number of instances to create.
                    times-attribute -- the name of the attribute that
                                       specifies the number of outgoing
                                       instances.
        """
        assert kwargs.has_key('times_attribute') or kwargs.has_key('times')
        Task.__init__(self, parent, name, **kwargs)
        self.times_attribute = kwargs.get('times_attribute', None)
        self.times           = kwargs.get('times',           None)
        self.thread_starter  = ThreadStart(parent, **kwargs)
        self.outputs.append(self.thread_starter)
        self.thread_starter._connect_notify(self)


    def connect(self, task):
        """
        Connect the *following* task to this one. In other words, the
        given task is added as an output task.

        task -- the task to connect to.
        """
        self.thread_starter.outputs.append(task)
        task._connect_notify(self.thread_starter)


    def _find_my_instance(self, job):
        for node in job.branch_tree:
            if node.thread_id != instance.thread_id:
                continue
            if node.task == self:
                return node
        return None


    def _get_activated_instances(self, instance, destination):
        """
        Returns the list of instances that were activated in the previous 
        call of execute(). Only returns instances that point towards the
        destination node, i.e. those which have destination as a 
        descendant.

        instance -- the instance of this task
        destination -- the child instance
        """
        node = destination._find_ancestor(self.thread_starter)
        return self.thread_starter._get_activated_instances(node, destination)


    def _get_activated_threads(self, instance):
        """
        Returns the list of threads that were activated in the previous 
        call of execute().

        instance -- the instance of this task
        """
        return instance.children


    def _on_trigger(self, instance):
        """
        May be called after execute() was already completed to create an
        additional outbound instance.
        """
        # Find a TaskInstance for this task.
        my_instance = self._find_my_instance(instance.job)
        for output in self.outputs:
            state        = TaskInstance.READY | TaskInstance.TRIGGERED
            new_instance = my_instance.add_child(output, state)


    def _predict_hook(self, instance):
        split_n = instance.get_attribute('split_n', self.times)
        if split_n is None:
            split_n = instance.get_attribute(self.times_attribute, 1)

        # Predict the outputs.
        outputs = []
        for i in range(split_n):
            outputs.append(self.thread_starter)
        if instance._is_definite():
            child_state = TaskInstance.FUTURE
        else:
            child_state = TaskInstance.LIKELY
        instance._update_children(outputs, child_state)


    def _on_complete_hook(self, instance):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        # Split, and remember the number of splits in the context data.
        split_n = self.times
        if split_n is None:
            split_n = instance.get_attribute(self.times_attribute)

        # Create the outgoing nodes.
        outputs = []
        for i in range(split_n):
            outputs.append(self.thread_starter)
        instance._update_children(outputs)
        return True
