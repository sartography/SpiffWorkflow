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
import Tasks
from mutex        import mutex
from Trackable    import Trackable
from TaskInstance import TaskInstance

class Job(Trackable):
    """
    This class implements the engine that executes a workflow.
    It is a essentially a facility for managing all branches.
    A Job is also the place that holds the attributes of a running workflow.
    """

    def __init__(self, workflow, **kwargs):
        """
        Constructor.
        """
        Trackable.__init__(self)
        assert workflow is not None
        self.workflow        = workflow
        self.attributes      = {}
        self.outer_job       = kwargs.get('parent', self)
        self.locks           = {}
        self.last_node       = None
        self.task_tree       = TaskInstance(self, Tasks.Task(workflow, 'Root'))
        self.success         = True
        self.debug           = False

        # Prevent the root node from being executed.
        self.task_tree.state = TaskInstance.COMPLETED
        start                = self.task_tree._add_child(workflow.start)

        workflow.start._predict(start)
        if not kwargs.has_key('parent'):
            start.task._update_state(start)
        #start.dump()


    def is_completed(self):
        """
        Returns True if the entire Job is completed, False otherwise.
        """
        mask = TaskInstance.NOT_FINISHED_MASK
        iter = TaskInstance.Iterator(self.task_tree, mask)
        try:
            next = iter.next()
        except:
            # No waiting nodes found.
            return True
        return False


    def _get_waiting_tasks(self):
        waiting = TaskInstance.Iterator(self.task_tree, TaskInstance.WAITING)
        return [w for w in waiting]


    def _instance_completed_notify(self, instance):
        if instance.get_name() == 'End':
            self.attributes.update(instance.get_attributes())
        # Update the state of every WAITING node.
        for node in self._get_waiting_tasks():
            node.task._update_state(node)
        if self.signal_subscribers('completed') == 0:
            # Since is_completed() is expensive it makes sense to bail
            # out if calling it is not necessary.
            return
        if self.is_completed():
            self.signal_emit('completed', self)


    def get_attribute(self, name, default = None):
        """
        Returns the value of the attribute with the given name, or the given
        default value if the attribute does not exist.

        name -- an attribute name (string)
        default -- the default value that is returned if the attribute does 
                   not exist.
        """
        return self.attributes.get(name, default)


    def get_mutex(self, name):
        if not self.locks.has_key(name):
            self.locks[name] = mutex()
        return self.locks[name]


    def cancel(self, success = False):
        """
        Cancels all open tasks in the job.

        success -- whether the Job should be marked as successfully completed
                   vs. unsuccessful
        """
        self.success = success
        cancel       = []
        mask         = TaskInstance.NOT_FINISHED_MASK
        for node in TaskInstance.Iterator(self.task_tree, mask):
            cancel.append(node)
        for node in cancel:
            node.cancel()
    

    def get_task_from_name(self, name):
        return self.workflow.tasks[name]


    def get_tasks(self, state = TaskInstance.ANY_MASK):
        """
        Returns a list of objects that each reference a task with the given
        state.
        """
        return [t for t in TaskInstance.Iterator(self.task_tree, state)]


    def complete_task_from_id(self, node_id):
        """
        Runs the given task.
        """
        if node_id is None:
            raise WorkflowException(self.workflow, 'node_id is None')
        for node in self.task_tree:
            if node.id == node_id:
                return node.complete()
        msg = 'A node with the given node_id (%s) was not found' % node_id
        raise WorkflowException(self.workflow, msg)


    def complete_next(self, pick_up = True):
        """
        Runs the next task.
        Returns True if completed, False otherwise.

        pick_up -- when True, this method attempts to choose the next task
                   not by searching beginning at the root, but by searching
                   from the position at which the last call of complete_next()
                   left off.
        """
        # Try to pick up where we left off.
        blacklist = []
        if pick_up and self.last_node is not None:
            try:
                iter = TaskInstance.Iterator(self.last_node, TaskInstance.READY)
                next = iter.next()
            except:
                next = None
            self.last_node = None
            if next is not None:
                if next.complete():
                    self.last_node = next
                    return True
                blacklist.append(next)

        # Walk through all waiting tasks.
        for node in TaskInstance.Iterator(self.task_tree, TaskInstance.READY):
            for blacklisted_node in blacklist:
                if node._is_descendant_of(blacklisted_node):
                    continue
            if node.complete():
                self.last_node = node
                return True
            blacklist.append(node)
        return False


    def complete_all(self, pick_up = True):
        """
        Runs all branches until completion.
        """
        while self.complete_next(pick_up):
            pass


    def get_dump(self):
        return self.task_tree.get_dump()


    def dump(self):
        return self.task_tree.dump()
