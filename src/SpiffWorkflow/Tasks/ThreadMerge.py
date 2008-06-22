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
from Task                       import Task
from Join                       import Join

class ThreadMerge(Join):
    """
    This class represents a task for synchronizing instances that were
    previously split using a a ThreadSplit.
    It has two or more incoming branches and one or more outputs.
    """

    def __init__(self, parent, name, split_task, **kwargs):
        """
        Constructor.
        
        parent -- a reference to the parent (Task)
        name -- a name for the pattern (string)
        split_task -- the name of the task that was previously used to split
                      the instance
        kwargs -- may contain the following keys:
                      threshold -- an integer that specifies how many incoming
                      branches need to complete before the task triggers.
                      When the limit is reached, the task fires but still
                      expects all other branches to complete.
                      cancel -- when set to True, remaining incoming branches
                      are cancelled as soon as the discriminator is activated.
        """
        assert split_task is not None
        Join.__init__(self, parent, name, split_task, **kwargs)


    def try_fire(self, instance):
        # If the threshold was already reached, there is nothing else to do.
        if instance._has_state(TaskInstance.COMPLETED):
            return False
        if instance._has_state(TaskInstance.READY):
            return True

        # Retrieve a list of all activated instances from the associated
        # task that did the conditional parallel split.
        split_node = instance._find_ancestor_from_name(self.split_task)
        if split_node is None:
            msg = 'Join with %s, which was not reached' % self.split_task
            raise WorkflowException(self, msg)
        nodes = split_node.task._get_activated_threads(split_node)

        # The default threshold is the number of threads that were started.
        threshold = valueof(instance, self.threshold)
        if threshold is None:
            threshold = len(nodes)

        # Look up which instances have already completed.
        waiting_nodes = []
        completed     = 0
        for node in nodes:
            # Refresh path prediction.
            node.task._predict(node)

            if self._branch_is_complete(node):
                completed += 1
            else:
                waiting_nodes.append(node)

        # If the threshold was reached, get ready to fire.
        if completed >= threshold:
            # If this is a cancelling join, cancel all incoming branches,
            # except for the one that just completed.
            if self.cancel_remaining:
                for node in waiting_nodes:
                    node.cancel()
            return True

        # We do NOT set the instance state to COMPLETED, because in
        # case all other incoming tasks get cancelled (or never reach
        # the ThreadMerge for other reasons, such as reaching a stub branch),
        # we need to revisit it.
        return False


    def _update_state_hook(self, instance):
        if not self.try_fire(instance):
            instance._set_state(TaskInstance.WAITING)
            return False

        split_task = instance.job.get_task_from_name(self.split_task)
        split_node = instance._find_ancestor(split_task)

        # Find the inbound node that was completed last.
        last_changed = None
        nodes        = []
        for node in split_node._find_any(self):
            if self.split_task and node._is_descendant_of(instance):
                continue
            changed = node.parent.last_state_change
            if last_changed is None \
              or changed > last_changed.parent.last_state_change:
                last_changed = node
            nodes.append(node)

        # Mark all nodes in this thread that reference this task as 
        # completed, except for the first one, which should be READY.
        for node in nodes:
            if node == last_changed:
                self.signal_emit('entered', instance.job, instance)
                node._ready()
            else:
                node.state = TaskInstance.COMPLETED
                node._drop_children()
        return False


    def _on_complete_hook(self, instance):
        """
        Runs the task. Should not be called directly.
        Returns True if completed, False otherwise.
        """
        return Task._on_complete_hook(self, instance)
