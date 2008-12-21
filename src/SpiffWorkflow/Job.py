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
from mutex       import mutex
from SpiffSignal import Trackable
from Task        import Task

class Job(Trackable):
    """
    The engine that executes a workflow.
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
        self.task_tree       = Task(self, Tasks.Simple(workflow, 'Root'))
        self.success         = True
        self.debug           = False

        # Prevent the root node from being executed.
        self.task_tree.state = Task.COMPLETED
        start                = self.task_tree._add_child(workflow.start)

        workflow.start._predict(start)
        if not kwargs.has_key('parent'):
            start.spec._update_state(start)
        #start.dump()


    def is_completed(self):
        """
        Returns True if the entire Job is completed, False otherwise.
        """
        mask = Task.NOT_FINISHED_MASK
        iter = Task.Iterator(self.task_tree, mask)
        try:
            next = iter.next()
        except:
            # No waiting nodes found.
            return True
        return False


    def _get_waiting_tasks(self):
        waiting = Task.Iterator(self.task_tree, Task.WAITING)
        return [w for w in waiting]


    def _task_completed_notify(self, task):
        if task.get_name() == 'End':
            self.attributes.update(task.get_attributes())
        # Update the state of every WAITING node.
        for node in self._get_waiting_tasks():
            node.spec._update_state(node)
        if self.signal_subscribers('completed') == 0:
            # Since is_completed() is expensive it makes sense to bail
            # out if calling it is not necessary.
            return
        if self.is_completed():
            self.signal_emit('completed', self)


    def _get_mutex(self, name):
        if not self.locks.has_key(name):
            self.locks[name] = mutex()
        return self.locks[name]


    def get_attribute(self, name, default = None):
        """
        Returns the value of the attribute with the given name, or the given
        default value if the attribute does not exist.

        @type  name: string
        @param name: An attribute name.
        @type  default: obj
        @param default: Return this value if the attribute does not exist.
        @rtype:  obj
        @return: The value of the attribute.
        """
        return self.attributes.get(name, default)


    def cancel(self, success = False):
        """
        Cancels all open tasks in the job.

        @type  success: boolean
        @param success: Whether the Job should be marked as successfully
                        completed.
        """
        self.success = success
        cancel       = []
        mask         = Task.NOT_FINISHED_MASK
        for node in Task.Iterator(self.task_tree, mask):
            cancel.append(node)
        for node in cancel:
            node.cancel()
    

    def get_task_from_name(self, name):
        """
        Returns the task with the given name.

        @type  name: string
        @param name: The name of the task.
        @rtype:  TaskSpec
        @return: The task with the given name.
        """
        return self.workflow.get_task_from_name(name)


    def get_tasks(self, state = Task.ANY_MASK):
        """
        Returns a list of Task objects with the given state.

        @type  state: integer
        @param state: A bitmask of states.
        @rtype:  list[Task]
        @return: A list of tasks.
        """
        return [t for t in Task.Iterator(self.task_tree, state)]


    def complete_task_from_id(self, node_id):
        """
        Runs the task with the given id.

        @type  node_id: integer
        @param node_id: The id of the Task object.
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

        @type  pick_up: boolean
        @param pick_up: When True, this method attempts to choose the next
                        task not by searching beginning at the root, but by
                        searching from the position at which the last call
                        of complete_next() left off.
        @rtype:  boolean
        @return: True if all tasks were completed, False otherwise.
        """
        # Try to pick up where we left off.
        blacklist = []
        if pick_up and self.last_node is not None:
            try:
                iter = Task.Iterator(self.last_node, Task.READY)
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
        for node in Task.Iterator(self.task_tree, Task.READY):
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
        Runs all branches until completion. This is a convinience wrapper
        around complete_next(), and the pick_up argument is passed along.

        @type  pick_up: boolean
        @param pick_up: Passed on to each call of complete_next().
        """
        while self.complete_next(pick_up):
            pass


    def get_dump(self):
        """
        Returns a complete dump of the current internal task tree for
        debugging.

        @rtype:  string
        @return: The debug information.
        """
        return self.task_tree.get_dump()


    def dump(self):
        """
        Like get_dump(), but prints the output to the terminal instead of
        returning it.
        """
        return self.task_tree.dump()
