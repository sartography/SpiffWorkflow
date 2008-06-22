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
import time
from Exception import WorkflowException

class TaskInstance(object):
    """
    This class implements a node for composing a tree that represents the
    taken/not yet taken path within the workflow.
    """
    FUTURE    =   1
    LIKELY    =   2
    MAYBE     =   4
    WAITING   =   8
    READY     =  16
    CANCELLED =  32
    COMPLETED =  64
    TRIGGERED = 128

    FINISHED_MASK      = CANCELLED | COMPLETED
    DEFINITE_MASK      = FUTURE | WAITING | READY | FINISHED_MASK
    PREDICTED_MASK     = FUTURE | LIKELY | MAYBE
    NOT_FINISHED_MASK  = PREDICTED_MASK | WAITING | READY
    ANY_MASK           = FINISHED_MASK | NOT_FINISHED_MASK

    state_names = {FUTURE:    'FUTURE',
                   WAITING:   'WAITING',
                   READY:     'READY',
                   CANCELLED: 'CANCELLED',
                   COMPLETED: 'COMPLETED',
                   LIKELY:    'LIKELY',
                   MAYBE:     'MAYBE',
                   TRIGGERED: 'TRIGGERED'}

    class Iterator(object):
        """
        This is a tree iterator that supports filtering such that a client
        may walk through all nodes that have a specific state.
        """
        def __init__(self, current, filter = None):
            """
            Constructor.
            """
            self.filter = filter
            self.path   = [current]


        def __iter__(self):
            return self


        def _next(self):
            # Make sure that the end is not yet reached.
            if len(self.path) == 0:
                raise StopIteration()

            # If the current node has children, the first child is the next item.
            # If the current node is LIKELY, and predicted nodes are not
            # specificly searched, we can ignore the children, because predicted
            # nodes should only have predicted children.
            current     = self.path[-1]
            ignore_node = False
            if self.filter is not None:
                search_predicted = self.filter   & TaskInstance.LIKELY != 0
                is_predicted     = current.state & TaskInstance.LIKELY != 0
                ignore_node      = is_predicted and not search_predicted
            if len(current.children) > 0 and not ignore_node:
                self.path.append(current.children[0])
                if self.filter is not None and current.state & self.filter == 0:
                    return None
                return current

            # Ending up here, this node has no children. Crop the path until we
            # reach a node that has unvisited children, or until we hit the end.
            while True:
                old_child = self.path.pop(-1)
                if len(self.path) == 0:
                    break

                # If this node has a sibling, choose it.
                parent = self.path[-1]
                pos    = parent.children.index(old_child)
                if len(parent.children) > pos + 1:
                    self.path.append(parent.children[pos + 1])
                    break
            if self.filter is not None and current.state & self.filter == 0:
                return None
            return current


        def next(self):
            # By using this loop we avoid an (expensive) recursive call.
            while True:
                next = self._next()
                if next is not None:
                    return next


    # Pool for assigning a unique id to every new TaskInstance.
    id_pool        = 0
    thread_id_pool = 0

    def __init__(self, job, task, parent = None):
        """
        Constructor.
        """
        assert job  is not None
        assert task is not None
        self.__class__.id_pool  += 1
        self.job                 = job
        self.parent              = parent
        self.children            = []
        self.state               = TaskInstance.FUTURE
        self.task                = task
        self.id                  = self.__class__.id_pool
        self.thread_id           = self.__class__.thread_id_pool
        self.last_state_change   = time.time()
        self.attributes          = {}
        self.internal_attributes = {}
        if parent is not None:
            self.parent._child_added_notify(self)


    def __iter__(self):
        return TaskInstance.Iterator(self)


    def __setstate__(self, dict):
        self.__dict__.update(dict)
        # If unpickled in the same Python process in which a workflow
        # (TaskInstance) is built through the API, we need to make sure
        # that there will not be any ID collisions.
        if dict['id'] >= self.__class__.id_pool:
            self.__class__.id_pool = dict['id']
        if dict['thread_id'] >= self.__class__.thread_id_pool:
            self.__class__.thread_id_pool = dict['thread_id']


    def _get_root(self):
        """
        Returns the top level parent.
        """
        if self.parent is None:
            return self
        return self.parent._get_root()


    def _get_depth(self):
        depth = 0
        node  = self.parent
        while node is not None:
            depth += 1
            node = node.parent
        return depth


    def _child_added_notify(self, child):
        """
        Called by another TaskInstance to let us know that a child was added.
        """
        assert child is not None
        self.children.append(child)


    def _drop_children(self):
        drop = []
        for child in self.children:
            if not child._is_finished():
                drop.append(child)
            else:
                child._drop_children()
        for node in drop:
            self.children.remove(node)


    def _set_state(self, state):
        self.state             = state
        self.last_state_change = time.time()


    def _has_state(self, state):
        """
        Returns True if the TaskInstance has the given state flag set.
        """
        return (self.state & state) != 0


    def _is_finished(self):
        return self.state & self.FINISHED_MASK != 0


    def _is_predicted(self):
        return self.state & self.PREDICTED_MASK != 0


    def _is_definite(self):
        return self.state & self.DEFINITE_MASK != 0


    def _add_child(self, task, state = FUTURE):
        """
        Adds a new child node and assigns the given task to the new node.

        task -- the task that is assigned to the new node.
        state -- the initial node state
        """
        if task is None:
            raise WorkflowException(self, '_add_child() requires a task.')
        if self._is_predicted() and state & self.PREDICTED_MASK == 0:
            msg = 'Attempt to add non-predicted child to predicted node'
            raise WorkflowException(self, msg)
        node           = TaskInstance(self.job, task, self)
        node.thread_id = self.thread_id
        if state == self.READY:
            node._ready()
        else:
            node.state = state
        return node


    def _assign_new_thread_id(self, recursive = True):
        """
        Assigns a new thread id to the node.
        Returns the new id.
        """
        self.__class__.thread_id_pool += 1
        self.thread_id = self.__class__.thread_id_pool
        if not recursive:
            return self.thread_id
        for node in self:
            node.thread_id = self.thread_id
        return self.thread_id


    def _update_children(self, tasks, state = None):
        """
        This method adds one child for each given task, unless that
        child already exists.
        The state of COMPLETED tasks is never changed.

        If this method is passed a state:
          - The state of TRIGGERED tasks is not changed.
          - The state for all children is set to the given value.

        If this method is not passed a state:
          The state for all children is updated by calling the child's
          _update_state() method.
          
        If the node currently has a child that is not given in the tasks, 
        the child is removed.
        It is an error if the node has a non-LIKELY child that is 
        not given in the tasks.

        task -- the list of tasks that may become children.
        state -- the state for newly added children
        """
        if tasks is None:
            raise WorkflowException(self, '"tasks" argument is None.')
        if type(tasks) != type([]):
            tasks = [tasks]

        # Create a list of all children that are no longer needed, and
        # set the state of all others.
        add    = tasks[:]
        remove = []
        for child in self.children:
            # Must not be TRIGGERED or COMPLETED.
            if child._has_state(TaskInstance.TRIGGERED):
                if state is None:
                    child.task._update_state(child)
                continue
            if child._is_finished():
                add.remove(child.task)
                continue

            # Check whether the item needs to be added or removed.
            if child.task not in add:
                if not self._is_definite():
                    msg = 'Attempt to remove non-predicted %s' % child.get_name()
                    raise WorkflowException(self, msg)
                remove.append(child)
                continue
            add.remove(child.task)

            # Update the state.
            if state is not None:
                child.state = state
            else:
                child.task._update_state(child)

        # Remove all children that are no longer specified.
        for child in remove:
            self.children.remove(child)

        # Add a new child for each of the remaining tasks.
        for task in add:
            if task.cancelled:
                continue
            if state is not None:
                self._add_child(task, state)
            else:
                node = self._add_child(task, self.LIKELY)
                task._update_state(node)


    def _set_likely_task(self, tasks):
        if type(tasks) != type([]):
            tasks = [tasks]
        for task in tasks:
            for child in self.children:
                if child.task != task:
                    continue
                if child._is_definite():
                    continue
                child._set_state(self.LIKELY)
                return


    def _is_descendant_of(self, parent):
        """
        Returns True if parent is in the list of ancestors, returns False
        otherwise.

        parent -- the parent that is searched in the ancestors.
        """
        if self.parent is None:
            return False
        if self.parent == parent:
            return True
        return self.parent._is_descendant_of(parent)


    def _find_child_of(self, parent_task):
        """
        Returns the ancestor that has a TaskInstance with the given Task
        as a parent.
        If no such ancestor was found, the root node is returned.

        parent_task -- the wanted parent Task
        """
        if self.parent is None:
            return self
        if self.parent.task == parent_task:
            return self
        return self.parent._find_child_of(parent_task)


    def _find_any(self, task):
        """
        Returns any descendants that have the given task assigned.

        task -- the wanted task
        """
        instances = []
        if self.task == task:
            instances.append(self)
        for node in self:
            if node.task != task:
                continue
            instances.append(node)
        return instances


    def _find_ancestor(self, task):
        """
        Returns the ancestor that has the given task assigned.
        If no such ancestor was found, the root node is returned.

        task -- the wanted task
        """
        if self.parent is None:
            return self
        if self.parent.task == task:
            return self.parent
        return self.parent._find_ancestor(task)


    def _find_ancestor_from_name(self, name):
        """
        Returns the ancestor that has a task with the given name assigned.
        Returns None if no such ancestor was found.

        task -- the wanted task
        """
        if self.parent is None:
            return None
        if self.parent.get_name() == name:
            return self.parent
        return self.parent._find_ancestor_from_name(name)


    def _ready(self):
        """
        Marks the node as ready for execution.
        """
        if self.state & self.COMPLETED != 0:
            return
        if self.state & self.CANCELLED != 0:
            return
        self._set_state(self.READY | (self.state & self.TRIGGERED))
        return self.task._on_ready(self)


    def get_name(self):
        return str(self.task.name)


    def get_description(self):
        return str(self.task.description)


    def get_state(self):
        """
        Returns this TaskInstance's state.
        """
        return self.state


    def get_state_name(self):
        """
        Returns a textual representation of this TaskInstance's state.
        """
        state_name = []
        for key, name in self.state_names.iteritems():
            if self.state & key != 0:
                state_name.append(name)
        return '|'.join(state_name)


    def get_property(self, name, default = None):
        """
        Returns the value of the property with the given name, or the given
        default value if the property does not exist.

        name -- a property name (string)
        default -- the default value that is returned if the property does 
                   not exist.
        """
        return self.task.get_property(name, default)


    def get_properties(self):
        """
        Returns a dictionary containing all properties.
        """
        return self.task.properties


    def _set_internal_attribute(self, **kwargs):
        """
        Defines the given attribute/value pairs.
        """
        self.internal_attributes.update(kwargs)


    def _get_internal_attribute(self, name, default = None):
        return self.internal_attributes.get(name, default)


    def set_attribute(self, **kwargs):
        """
        Defines the given attribute/value pairs.
        """
        self.attributes.update(kwargs)


    def _inherit_attributes(self):
        """
        Inherits the attributes from the parent.
        """
        self.set_attribute(**self.parent.attributes)


    def get_attribute(self, name, default = None):
        """
        Returns the value of the attribute with the given name, or the given
        default value if the attribute does not exist.

        name -- an attribute name (string)
        default -- the default value that is returned if the attribute does 
                   not exist.
        """
        return self.attributes.get(name, default)


    def get_attributes(self):
        return self.attributes


    def cancel(self):
        """
        Cancels the item if it was not yet completed, and removes
        any children that are LIKELY.
        """
        if self._is_finished():
            for child in self.children:
                child.cancel()
            return
        self._set_state(self.CANCELLED | (self.state & self.TRIGGERED))
        self._drop_children()
        return self.task._on_cancel(self)


    def complete(self):
        """
        Called by the associated task to let us know that its state
        has changed (e.g. from FUTURE to COMPLETED.)
        """
        self._set_state(self.COMPLETED | (self.state & self.TRIGGERED))
        return self.task._on_complete(self)


    def trigger(self, *args):
        """
        If recursive is True, the state is applied to the tree recursively.
        """
        self.task._on_trigger(self, *args)


    def get_dump(self, indent = 0, recursive = True):
        """
        Returns the subtree as a string for debugging.
        """
        dbg  = (' ' * indent * 2)
        dbg += '%s/'                 % self.id
        dbg += '%s:'                 % self.thread_id
        dbg += ' TaskInstance of %s' % self.get_name()
        dbg += ' State: %s'          % self.get_state_name()
        dbg += ' Children: %s'       % len(self.children)
        if recursive:
            for child in self.children:
                dbg += '\n' + child.get_dump(indent + 1)
        return dbg


    def dump(self, indent = 0):
        """
        Prints the subtree as a string for debugging.
        """
        print self.get_dump()
