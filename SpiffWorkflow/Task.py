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
import logging
import time

from SpiffWorkflow.exceptions import WorkflowException

LOG = logging.getLogger(__name__)


class Task(object):
    """
    Used internally for composing a tree that represents the path that
    is taken (or predicted) within the workflow.

    Each Task has a state. For an explanation, consider the following task
    specification::

                                    ,-> Simple (default choice)
        StartTask -> ExclusiveChoice
                                    `-> Simple

    The initial task tree for this specification looks like so::

                                                   ,-> Simple LIKELY
        StartTask WAITING -> ExclusiveChoice FUTURE
                                                   `-> Simple MAYBE

    The following states may exist::

        - FUTURE: The task will definitely be reached in the future,
        regardless of which choices the user makes within the workflow.

        - LIKELY: The task may or may not be reached in the future. It
        is likely because the specification lists it as the default
        option for the ExclusiveChoice.

        - MAYBE: The task may or may not be reached in the future. It
        is not LIKELY, because the specification does not list it as the
        default choice for the ExclusiveChoice.

        - WAITING: The task is still waiting for an event before it
        completes. For example, a Join task will be WAITING until all
        predecessors are completed.

        - READY: The conditions for completing the task are now satisfied.
        Usually this means that all predecessors have completed and the
        task may now be completed using
        L{Workflow.complete_task_from_id()}.

        - CANCELLED: The task was cancelled by a CancelTask or
        CancelWorkflow task.

        - COMPLETED: The task was regularily completed.

        - TRIGGERED: This is an extra flag that may be used in connection
        with the other states. It means that the task was created at
        runtime, for example by a Trigger or MultiInstance task.

    Note that the LIKELY and MAYBE tasks are merely predicted/guessed, so
    those tasks may be removed from the tree at runtime later. They are
    created to allow for visualizing the workflow at a time where
    the required decisions have not yet been made.
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
        may walk through all tasks that have a specific state.
        """
        def __init__(self, current, filter=None):
            """
            Constructor.
            """
            self.filter = filter
            self.path = [current]

        def __iter__(self):
            return self

        def _next(self):
            # Make sure that the end is not yet reached.
            if len(self.path) == 0:
                raise StopIteration()

            # If the current task has children, the first child is the next item.
            # If the current task is LIKELY, and predicted tasks are not
            # specificly searched, we can ignore the children, because predicted
            # tasks should only have predicted children.
            current = self.path[-1]
            ignore_task = False
            if self.filter is not None:
                search_predicted = self.filter & Task.LIKELY != 0
                is_predicted = current.state & Task.LIKELY != 0
                ignore_task = is_predicted and not search_predicted
            if current.children and not ignore_task:
                self.path.append(current.children[0])
                if self.filter is not None and current.state & self.filter == 0:
                    return None
                return current

            # Ending up here, this task has no children. Crop the path until we
            # reach a task that has unvisited children, or until we hit the end.
            while True:
                old_child = self.path.pop(-1)
                if len(self.path) == 0:
                    break

                # If this task has a sibling, choose it.
                parent = self.path[-1]
                pos = parent.children.index(old_child)
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


    # Pool for assigning a unique thread id to every new Task.
    thread_id_pool = 0

    def __init__(self, workflow, task_spec, parent=None):
        """
        Constructor.
        """
        assert workflow  is not None
        assert task_spec is not None
        self.workflow            = workflow
        self.parent              = parent
        self.children            = []
        self._state              = Task.FUTURE
        self.state_history       = [Task.FUTURE]
        self.log                 = []
        self.task_spec           = task_spec
        self.id                  = workflow.task_id_assigner.get_new_id()
        self.thread_id           = self.__class__.thread_id_pool
        self.last_state_change   = time.time()
        self.attributes          = {}
        self.internal_attributes = {}
        if parent is not None:
            self.parent._child_added_notify(self)

    def _getstate(self):
        return self._state

    def _setstate(self, value):
        if self._state != value:
            if __debug__:
                old = self.get_state_name()
            self._state = value
            if __debug__:
                self.log.append("Moving '%s' from %s to %s" % (self.get_name(),
                        old, self.get_state_name()))
            self.state_history.append(value)
            LOG.debug("Moving '%s' (spec=%s) from %s to %s" % (self.get_name(),
                        self.task_spec.name, old, self.get_state_name()))

    def _delstate(self):
        del self._state

    state = property(_getstate, _setstate, _delstate, "State property.")

    def __iter__(self):
        return Task.Iterator(self)

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        # If unpickled in the same Python process in which a workflow
        # (Task) is built through the API, we need to make sure
        # that there will not be any ID collisions.
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
        task = self.parent
        while task is not None:
            depth += 1
            task = task.parent
        return depth

    def _child_added_notify(self, child):
        """
        Called by another Task to let us know that a child was added.
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
        for task in drop:
            self.children.remove(task)

    def _set_state(self, state):
        self.state = state
        self.last_state_change = time.time()

    def _has_state(self, state):
        """
        Returns True if the Task has the given state flag set.
        """
        return (self.state & state) != 0

    def _is_finished(self):
        return self.state & self.FINISHED_MASK != 0

    def _is_predicted(self):
        return self.state & self.PREDICTED_MASK != 0

    def _is_definite(self):
        return self.state & self.DEFINITE_MASK != 0

    def _add_child(self, task_spec, state=FUTURE):
        """
        Adds a new child and assigns the given TaskSpec to it.

        @type  task_spec: TaskSpec
        @param task_spec: The task spec that is assigned to the new child.
        @type  state: integer
        @param state: The bitmask of states for the new child.
        @rtype:  Task
        @return: The new child task.
        """
        if task_spec is None:
            raise ValueError(self, '_add_child() requires a TaskSpec')
        if self._is_predicted() and state & self.PREDICTED_MASK == 0:
            msg = 'Attempt to add non-predicted child to predicted task'
            raise WorkflowException(self, msg)
        task = Task(self.workflow, task_spec, self)
        task.thread_id = self.thread_id
        if state == self.READY:
            task._ready()
        else:
            task.state = state
        return task

    def _assign_new_thread_id(self, recursive=True):
        """
        Assigns a new thread id to the task.

        @type  recursive: boolean
        @param recursive: Whether to assign the id to children recursively.
        @rtype:  boolean
        @return: The new thread id.
        """
        self.__class__.thread_id_pool += 1
        self.thread_id = self.__class__.thread_id_pool
        if not recursive:
            return self.thread_id
        for child in self:
            child.thread_id = self.thread_id
        return self.thread_id

    def _update_children(self, task_specs, state=None):
        """
        This method adds one child for each given TaskSpec, unless that
        child already exists.
        The state of COMPLETED tasks is never changed.

        If this method is passed a state:
          - The state of TRIGGERED tasks is not changed.
          - The state for all children is set to the given value.

        If this method is not passed a state:
          - The state for all children is updated by calling the child's
          _update_state() method.

        If the task currently has a child that is not given in the TaskSpec,
        the child is removed.
        It is an error if the task has a non-LIKELY child that is
        not given in the TaskSpecs.

        @type  task_specs: list(TaskSpec)
        @param task_specs: The list of task specs that may become children.
        @type  state: integer
        @param state: The bitmask of states for newly added children.
        """
        LOG.debug("Updating children for %s" % self.get_name())
        if task_specs is None:
            raise ValueError('"task_specs" argument is None')
        if type(task_specs) != type([]):
            task_specs = [task_specs]

        # Create a list of all children that are no longer needed, and
        # set the state of all others.
        add = task_specs[:]
        remove = []
        for child in self.children:
            # Must not be TRIGGERED or COMPLETED.
            if child._has_state(Task.TRIGGERED):
                if state is None:
                    child.task_spec._update_state(child)
                continue
            if child._is_finished():
                add.remove(child.task_spec)
                continue

            # Check whether the item needs to be added or removed.
            if child.task_spec not in add:
                if not self._is_definite():
                    msg = 'Attempt to remove non-predicted %s' % child.get_name()
                    raise WorkflowException(self, msg)
                remove.append(child)
                continue
            add.remove(child.task_spec)

            # Update the state.
            if state is not None:
                child.state = state
            else:
                child.task_spec._update_state(child)

        # Remove all children that are no longer specified.
        for child in remove:
            self.children.remove(child)

        # Add a new child for each of the remaining tasks.
        for task_spec in add:
            if state is not None:
                self._add_child(task_spec, state)
            else:
                child = self._add_child(task_spec, self.LIKELY)
                task_spec._update_state(child)

    def _set_likely_task(self, task_specs):
        if type(task_specs) != type([]):
            task_specs = [task_specs]
        for task_spec in task_specs:
            for child in self.children:
                if child.task_spec != task_spec:
                    continue
                if child._is_definite():
                    continue
                child._set_state(self.LIKELY)
                return

    def _is_descendant_of(self, parent):
        """
        Returns True if parent is in the list of ancestors, returns False
        otherwise.

        @type  parent: Task
        @param parent: The parent that is searched in the ancestors.
        @rtype:  boolean
        @return: Whether the parent was found.
        """
        if self.parent is None:
            return False
        if self.parent == parent:
            return True
        return self.parent._is_descendant_of(parent)

    def _find_child_of(self, parent_task_spec):
        """
        Returns the ancestor that has a task with the given task spec
        as a parent.
        If no such ancestor was found, the root task is returned.

        @type  parent_task_spec: TaskSpec
        @param parent_task_spec: The wanted ancestor.
        @rtype:  Task
        @return: The child of the given ancestor.
        """
        if self.parent is None:
            return self
        if self.parent.task_spec == parent_task_spec:
            return self
        return self.parent._find_child_of(parent_task_spec)

    def _find_any(self, task_spec):
        """
        Returns any descendants that have the given task spec assigned.

        @type  task_spec: TaskSpec
        @param task_spec: The wanted task spec.
        @rtype:  list(Task)
        @return: The tasks objects that are attached to the given task spec.
        """
        tasks = []
        if self.task_spec == task_spec:
            tasks.append(self)
        for child in self:
            if child.task_spec != task_spec:
                continue
            tasks.append(child)
        return tasks

    def _find_ancestor(self, task_spec):
        """
        Returns the ancestor that has the given task spec assigned.
        If no such ancestor was found, the root task is returned.

        @type  task_spec: TaskSpec
        @param task_spec: The wanted task spec.
        @rtype:  Task
        @return: The ancestor.
        """
        if self.parent is None:
            return self
        if self.parent.task_spec == task_spec:
            return self.parent
        return self.parent._find_ancestor(task_spec)

    def _find_ancestor_from_name(self, name):
        """
        Returns the ancestor that has a task with the given name assigned.
        Returns None if no such ancestor was found.

        @type  name: str
        @param name: The name of the wanted task.
        @rtype:  Task
        @return: The ancestor.
        """
        if self.parent is None:
            return None
        if self.parent.get_name() == name:
            return self.parent
        return self.parent._find_ancestor_from_name(name)

    def _ready(self):
        """
        Marks the task as ready for execution.
        """
        if self.state & self.COMPLETED != 0:
            return
        if self.state & self.CANCELLED != 0:
            return
        self._set_state(self.READY | (self.state & self.TRIGGERED))
        return self.task_spec._on_ready(self)

    def get_name(self):
        return str(self.task_spec.name)

    def get_description(self):
        return str(self.task_spec.description)

    def get_state(self):
        """
        Returns this Task's state.
        """
        return self.state

    def get_state_name(self):
        """
        Returns a textual representation of this Task's state.
        """
        state_name = []
        for key, name in self.state_names.iteritems():
            if self.state & key != 0:
                state_name.append(name)
        return '|'.join(state_name)

    def get_property(self, name, default=None):
        """
        Returns the value of the property with the given name, or the given
        default value if the property does not exist.

        @type  name: str
        @param name: A property name.
        @type  default: obj
        @param default: Return this value if the property does not exist.
        @rtype:  obj
        @return: The value of the property.
        """
        return self.task_spec.get_property(name, default)

    def get_properties(self):
        """
        Returns a dictionary containing all properties.

        @rtype:  dict
        @return: Maps property names to values.
        """
        return self.task_spec.properties

    def _set_internal_attribute(self, **kwargs):
        """
        Defines the given attribute/value pairs.
        """
        self.internal_attributes.update(kwargs)

    def _get_internal_attribute(self, name, default=None):
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

    def get_attribute(self, name, default=None):
        """
        Returns the value of the attribute with the given name, or the given
        default value if the attribute does not exist.

        @type  name: str
        @param name: An attribute name.
        @type  default: obj
        @param default: Return this value if the attribute does not exist.
        @rtype:  obj
        @return: The value of the attribute.
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
        return self.task_spec._on_cancel(self)

    def complete(self):
        """
        Called by the associated task to let us know that its state
        has changed (e.g. from FUTURE to COMPLETED.)
        """
        self._set_state(self.COMPLETED | (self.state & self.TRIGGERED))
        return self.task_spec._on_complete(self)

    def trigger(self, *args):
        """
        If recursive is True, the state is applied to the tree recursively.
        """
        self.task_spec._on_trigger(self, *args)

    def get_dump(self, indent=0, recursive=True):
        """
        Returns the subtree as a string for debugging.

        @rtype:  str
        @return: The debug information.
        """
        dbg  = (' ' * indent * 2)
        dbg += '%s/'           % self.id
        dbg += '%s:'           % self.thread_id
        dbg += ' Task of %s'   % self.get_name()
        dbg += ' State: %s'    % self.get_state_name()
        dbg += ' Children: %s' % len(self.children)
        if recursive:
            for child in self.children:
                dbg += '\n' + child.get_dump(indent + 1)
        return dbg

    def dump(self, indent=0):
        """
        Prints the subtree as a string for debugging.
        """
        print self.get_dump()
