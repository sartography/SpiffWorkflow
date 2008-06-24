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

class Join(TaskSpec):
    """
    This class represents a task for synchronizing instances that were
    previously split using a conditional task, such as MultiChoice.
    It has two or more incoming branches and one or more outputs.
    """

    def __init__(self, parent, name, split_task = None, **kwargs):
        """
        Constructor.
        
        parent -- a reference to the parent (TaskSpec)
        name -- a name for the pattern (string)
        split_task -- the task that was previously used to split the
                          instance
        kwargs -- may contain the following keys:
                      threshold -- an integer that specifies how many incoming
                      branches need to complete before the task triggers.
                      When the limit is reached, the task fires but still
                      expects all other branches to complete.
                      read from the attribute with the given name at runtime.
                      cancel -- when set to True, remaining incoming branches
                      are cancelled as soon as the discriminator is activated.
        """
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.split_task       = split_task
        self.threshold        = kwargs.get('threshold', None)
        self.cancel_remaining = kwargs.get('cancel',    False)


    def _branch_is_complete(self, instance):
        # Determine whether that branch is now completed by checking whether
        # it has any waiting items other than myself in it.
        skip  = None
        for node in TaskInstance.Iterator(instance, instance.NOT_FINISHED_MASK):
            # If the current node is a child of myself, ignore it.
            if skip is not None and node._is_descendant_of(skip):
                continue
            if node.task == self:
                skip = node
                continue
            return False
        return True


    def _branch_may_merge_at(self, instance):
        for node in instance:
            # Ignore nodes that were created by a trigger.
            if node._has_state(TaskInstance.TRIGGERED):
                continue
            # Merge found.
            if node.task == self:
                return True
            # If the node is predicted with less outputs than he has
            # children, that means the prediction may be incomplete (for
            # example, because a prediction is not yet possible at this time).
            if not node._is_definite() \
                and len(node.task.outputs) > len(node.children):
                return True
        return False


    def _fire(self, instance, waiting_nodes):
        """
        Fire, and cancel remaining tasks, if so requested.
        """
        # If this is a cancelling join, cancel all incoming branches,
        # except for the one that just completed.
        if self.cancel_remaining:
            for node in waiting_nodes:
                node.cancel()


    def _try_fire_unstructured(self, instance, force = False):
        # If the threshold was already reached, there is nothing else to do.
        if instance._has_state(TaskInstance.COMPLETED):
            return False
        if instance._has_state(TaskInstance.READY):
            return True

        # The default threshold is the number of inputs.
        threshold = valueof(instance, self.threshold)
        if threshold is None:
            threshold = len(self.inputs)

        # Look at the tree to find all places where this task is used.
        nodes = []
        for task in self.inputs:
            for node in instance.job.task_tree:
                if node.thread_id != instance.thread_id:
                    continue
                if node.task != task:
                    continue
                nodes.append(node)

        # Look up which instances have already completed.
        waiting_nodes = []
        completed     = 0
        for node in nodes:
            if node.parent is None or node._has_state(TaskInstance.COMPLETED):
                completed += 1
            else:
                waiting_nodes.append(node)

        # If the threshold was reached, get ready to fire.
        if force or completed >= threshold:
            self._fire(instance, waiting_nodes)
            return True

        # We do NOT set the instance state to COMPLETED, because in
        # case all other incoming tasks get cancelled (or never reach
        # the Join for other reasons, such as reaching a stub branch), we
        # we need to revisit it.
        return False


    def _try_fire_structured(self, instance, force = False):
        # If the threshold was already reached, there is nothing else to do.
        if instance._has_state(TaskInstance.READY):
            return True
        if instance._has_state(TaskInstance.COMPLETED):
            return False

        # Retrieve a list of all activated instances from the associated
        # task that did the conditional parallel split.
        split_node = instance._find_ancestor_from_name(self.split_task)
        if split_node is None:
            msg = 'Join with %s, which was not reached' % self.split_task
            raise WorkflowException(self, msg)
        nodes = split_node.task._get_activated_instances(split_node, instance)

        # The default threshold is the number of branches that were started.
        threshold = valueof(instance, self.threshold)
        if threshold is None:
            threshold = len(nodes)

        # Look up which instances have already completed.
        waiting_nodes = []
        completed     = 0
        for node in nodes:
            # Refresh path prediction.
            node.task._predict(node)

            if not self._branch_may_merge_at(node):
                completed += 1
            elif self._branch_is_complete(node):
                completed += 1
            else:
                waiting_nodes.append(node)

        # If the threshold was reached, get ready to fire.
        if force or completed >= threshold:
            self._fire(instance, waiting_nodes)
            return True

        # We do NOT set the instance state to COMPLETED, because in
        # case all other incoming tasks get cancelled (or never reach
        # the Join for other reasons, such as reaching a stub branch), we
        # need to revisit it.
        return False


    def try_fire(self, instance, force = False):
        if self.split_task is None:
            return self._try_fire_unstructured(instance, force)
        return self._try_fire_structured(instance, force)


    def _do_join(self, instance):
        if self.split_task:
            split_task = instance.job.get_task_from_name(self.split_task)
            split_node = instance._find_ancestor(split_task)
        else:
            split_node = instance.job.task_tree

        # Find the inbound node that was completed last.
        last_changed = None
        thread_nodes = []
        for node in split_node._find_any(self):
            if node.thread_id != instance.thread_id:
                continue
            if self.split_task and node._is_descendant_of(instance):
                continue
            changed = node.parent.last_state_change
            if last_changed is None \
              or changed > last_changed.parent.last_state_change:
                last_changed = node
            thread_nodes.append(node)

        # Mark all nodes in this thread that reference this task as 
        # completed, except for the first one, which should be READY.
        for node in thread_nodes:
            if node == last_changed:
                self.signal_emit('entered', instance.job, instance)
                node._ready()
            else:
                node.state = TaskInstance.COMPLETED
                node._drop_children()
        return False


    def _on_trigger(self, instance):
        """
        May be called to fire the Join before the incoming branches are
        completed.
        """
        for node in instance.job.task_tree._find_any(self):
            if node.thread_id != instance.thread_id:
                continue
            return self._do_join(node)


    def _update_state_hook(self, instance):
        if not self.try_fire(instance):
            instance.state = TaskInstance.WAITING
            return False
        return self._do_join(instance)


    def _on_complete_hook(self, instance):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        return TaskSpec._on_complete_hook(self, instance)
