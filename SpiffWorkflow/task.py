# Copyright (C) 2007 Samuel Abels, 2023 Sartography
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

from copy import deepcopy

import logging
import time
from uuid import uuid4

from .util.task import TaskState, TaskFilter, TaskIterator
from .util.deep_merge import DeepMerge
from .exceptions import WorkflowException

logger = logging.getLogger('spiff.task')


class Task(object):
    """Used internally for composing a tree that represents possible paths through a Workflow.

    Attributes:
        id (UUID): a unique identifierfor this task
        workflow (`Workflow`): the workflow associated with this task
        parent (`Task`): the parent of this task
        children (list(`Task`)): the children of this task
        triggered (bool): True if the task is not part of output specification of the task spec
        task_spec (`TaskSpec`): the spec associated with this task
        thread_id (int): a thread id for this task
        data (dict): a dictionary containing data for this task
        internal_data (dict): a dictionary containing information relevant to the task state or execution
        last_state_change (float): the timestamp when this task last changed state
        thread_id (int): a thread identifier

    Note:
        The `thread_id` attribute might be more accurately named `branch_id`, as it pertains only to workflow
        structure (eg, branches between split and merge tasks) rather than anything to do with threaded execution.

    Warning:
        The `data` attribute represents the state of the data as this particular task is executed. It is copied from
        its parent when the task is updated (this can behavior can be modified in the `TaskSpec.update` method).
        This can be VERY resource intensive in large workflows or with lots of data.
    """

    thread_id_pool = 0    # Pool for assigning a unique thread id to every new Task.

    def __init__(self, workflow, task_spec, parent=None, state=TaskState.MAYBE, id=None):
        """
        Args:
            workflow (`Workflow`): the workflow this task should be added to
            task_spec (`TaskSpec`): the spec associated with this task

        Keyword Args:
            parent (`Task`): the parent of this task
            state (`TaskState`): the state of this task (default MAYBE)
            id: an optional id (defaults to a random UUID)
        """
        self.id = id or uuid4()
        workflow.tasks[self.id] = self
        self.workflow = workflow

        self._parent = parent.id if parent is not None else None
        self._children = []
        self._state = state

        self.triggered = False
        self.task_spec = task_spec

        self.thread_id = self.__class__.thread_id_pool
        self.data = {}
        self.internal_data = {}
        self.last_state_change = time.time()
        if parent is not None:
            self.parent._child_added_notify(self)

    @property
    def state(self):
        """`TaskState`: this task's state

        Raises:
            `WorkflowException`: If setting the state results in a "backwards" state change.
        """
        return self._state

    @state.setter
    def state(self, value):
        if value < self._state:
            raise WorkflowException(
                'state went from %s to %s!' % (TaskState.get_name(self._state), TaskState.get_name(value)),
                task_spec=self.task_spec
            )
        self._set_state(value)

    @property
    def parent(self):
        """`Task`: This task's parent task"""
        return self.workflow.tasks.get(self._parent)

    @parent.setter
    def parent(self, task):
        self._parent = task.id if task is not None else None
    
    @property
    def children(self):
        """list(`Task`): This task's child tasks"""
        return [self.workflow.tasks.get(child) for child in self._children]
    
    @children.setter
    def children(self, tasks):
        self._children = [child.id for child in tasks]

    @property
    def depth(self):
        """The task's depth"""
        depth = 0
        task = self.parent
        while task is not None:
            depth += 1
            task = task.parent
        return depth

    def has_state(self, state):
        """Check the state of this task.

        Args:
            state (`TaskState`): the state to check

        Returns:
            bool: `True` is the task has the state or mask
        """
        return (self._state & state) != 0

    def set_data(self, **kwargs):
        """Defines the given attribute/value pairs in this task's data."""
        self.data.update(kwargs)
 
    def get_data(self, name, default=None):
        """Returns the value of the data field with the given name, or the given
        default value if the data field does not exist.

        Args:
            name (str): the dictionary key to return
            default (obj): a default value to return if the key does not exist

        Returns:
            the value of the key, or the default
        """
        return self.data.get(name, default)

    def reset_branch(self, data):
        """Removes all descendendants of this task and set this task to be runnable.

        Args:
            data (dict): set the task data to these values (if None, inherit from parent task)

        Returns:
            list(`Task`): tasks removed from the tree
        """
        logger.info(f'Branch reset', extra=self.collect_log_extras())
        self.internal_data = {}
        self.data = deepcopy(self.parent.data) if data is None else data    
        descendants = [t for t in self]
        self._drop_children(force=True)
        self._set_state(TaskState.FUTURE)
        self.task_spec._predict(self, mask=TaskState.PREDICTED_MASK|TaskState.FUTURE)
        self.task_spec._update(self)
        return descendants[1:] if len(descendants) > 1 else []

    def is_descendant_of(self, task):
        """Checks whether a task is an ancestor of this task.

        Args:
            task (`Task`): the potential ancestor

        Returns:
            bool: whether the task is an ancestor of this task
        """
        if self.parent is None:
            return False
        if self.parent == task:
            return True
        return self.parent.is_descendant_of(task)

    def find_ancestor(self, spec_name):
        """Search for an ancestor that has a task with a spec of the specified name.

        Args:
            spec_name (str): the name of the spec associated with the task

        Returns:
            `Task`: the first result (or None, if no matching task was found)
        """
        if self.parent is None:
            return None
        if self.parent.task_spec.name == spec_name:
            return self.parent
        return self.parent.find_ancestor(spec_name)

    def _add_child(self, task_spec, state=TaskState.MAYBE):
        """Adds a new child and assigns the given TaskSpec to it.

        Args:
            task_spec (`TaskSpec`): the spec associated with the child task
            state (`TaskState`): the state to assign

        Returns:
            `Task`: the new child

        Raises:
            `WorkflowException`: if an invalid task task addition occurs
        """
        if self.has_state(TaskState.PREDICTED_MASK) and state & TaskState.PREDICTED_MASK == 0:
            raise WorkflowException('Attempt to add non-predicted child to predicted task', task_spec=self.task_spec)
        task = Task(self.workflow, task_spec, self, state=state)
        task.thread_id = self.thread_id
        if state == TaskState.READY:
            task._ready()
        return task

    def _sync_children(self, task_specs, state=TaskState.MAYBE):
        """Syncs the task's children with the given list of task specs. 
    
        - Add one child for each given `TaskSpec`, unless that child already exists.
        - Remove all children for which there is no spec in the given list, unless it is a "triggered" task.

        Notes:
           It is an error if the task has a non-predicted child that is not given in the TaskSpecs.

        Args:
            task_spec (list(`TaskSpec`)): the list of task specs that may become children
            state (`TaskState`): the state to assign
        """
        if task_specs is None:
            raise ValueError('"task_specs" argument is None')
        new_children = task_specs[:]

        # Create a list of all children that are no longer needed.
        unneeded_children = []
        for child in self.children:
            if child.triggered:
                # Triggered tasks are never removed.
                pass
            elif child.task_spec in new_children:
                # If the task already exists, remove it from to-be-added and update its state
                new_children.remove(child.task_spec)
                if child.has_state(TaskState.NOT_FINISHED_MASK):
                    child._set_state(state)
            else:
                if child.has_state(TaskState.DEFINITE_MASK):
                    # Definite tasks must not be removed, so they HAVE to be in the given task spec list.
                    raise WorkflowException(f'removal of non-predicted child {child}', task_spec=self.task_spec)
                unneeded_children.append(child)

        # Update children accordingly
        for child in unneeded_children:
            self.workflow._remove_task(child.id)
        for task_spec in new_children:
            self._add_child(task_spec, state)

    def _child_added_notify(self, child):
        """Called by another task to let us know that a child was added."""
        self._children.append(child.id)

    def _drop_children(self, force=False):
        """Remove this task's children from the tree"""

        drop = []
        for child in self.children:
            if force or child.has_state(TaskState.NOT_FINISHED_MASK):
                drop.append(child)
            else:
                child._drop_children()

        for task in drop:
            self.workflow._remove_task(task.id)

    def _set_state(self, value):
        """Force set the state on a task"""

        if value != self.state:
            self.last_state_change = time.time()
            self._state = value
            logger.info(f'State changed to {TaskState.get_name(value)}', extra=self.collect_log_extras())
        else:
            logger.debug(f'State set to {TaskState.get_name(value)}', extra=self.collect_log_extras())

    def _assign_new_thread_id(self, recursive=True):
        """Assigns a new thread id to the task."""

        self.__class__.thread_id_pool += 1
        self.thread_id = self.__class__.thread_id_pool
        if not recursive:
            return self.thread_id
        for child in self:
            child.thread_id = self.thread_id
        return self.thread_id

    def _inherit_data(self):
        """Copies the data from the parent."""
        self.set_data(**deepcopy(self.parent.data))

    def _set_internal_data(self, **kwargs):
        """Defines the given attribute/value pairs in this task's internal data."""
        self.internal_data.update(kwargs)

    def _get_internal_data(self, name, default=None):
        """Retrieves an internal data field"""
        return self.internal_data.get(name, default)

    def _ready(self):
        """Marks the task as ready for execution."""
        if self.has_state(TaskState.COMPLETED) or self.has_state(TaskState.CANCELLED):
            return
        self._set_state(TaskState.READY)
        self.task_spec._on_ready(self)

    def run(self):
        """Execute the task.

        Call's the task spec's `TaskSpec.run` method and checks the return value.

        If the return value is
        - `True`: mark the task COMPLETE
        - `False`: mark the task in ERROR
        - `None`: mark the task STARTED

        Returns:
            bool: the value returned by the `TaskSpec`'s run method

        See `TaskState` for more information about states.
        """
        start = time.time()
        retval = self.task_spec._run(self)
        if retval is None:
            self._set_state(TaskState.STARTED)
        elif retval is False:
            self.error()
        else:
            self.complete()
        return retval

    def cancel(self):
        """Cancels the item if it was not yet completed; recursively cancels its children."""
        if self.has_state(TaskState.FINISHED_MASK):
            for child in self.children:
                child.cancel()
        else:
            self._set_state(TaskState.CANCELLED)
            self._drop_children()
            self.task_spec._on_cancel(self)

    def complete(self):
        """Marks this task complete."""
        self._set_state(TaskState.COMPLETED)
        self.task_spec._on_complete(self)
        self.workflow.last_task = self

    def error(self):
        """Marks this task as error."""
        self._set_state(TaskState.ERROR)
        self.task_spec._on_error(self)

    def trigger(self, *args):
        """Call the `TaskSpec`'s trigger method.

        Args are passed directly to the task spec.
        """
        self.task_spec._on_trigger(self, *args)

    def collect_log_extras(self, dct=None):
        """Return logging details for this task"""
        extra = dct or {}
        extra.update({
            'workflow_spec': self.workflow.spec.name,
            'task_spec': self.task_spec.name,
            'task_id': self.id,
            'task_type': self.task_spec.__class__.__name__,
            'state': TaskState.get_name(self._state),
            'last_state_change': self.last_state_change,
        })
        if logger.level < 20:
            extra.update({
                'data': self.data if logger.level < 20 else None,
                'internal_data': self.internal_data if logger.level < 20 else None,
            })
        return extra

    def __iter__(self):
        return TaskIterator(self)

    def __repr__(self):
        return f'<Task object ({self.task_spec.name}) in state {TaskState.get_name(self.state)} with id {self.id}>'

    # I will probably remove these methods at some point because I hate them

    def get_dump(self, indent=0, recursive=True):
        """Returns the subtree as a string for debugging.

        Returns:
            str: a tree view of the task (and optionally its children)
        """
        dbg = (' ' * indent * 2)
        dbg += '%s/' % self.id
        dbg += '%s:' % self.thread_id
        dbg += ' Task of %s' % self.task_spec.name
        if self.task_spec.description:
            dbg += ' (%s)' % self.task_spec.description
        dbg += ' State: %s' % TaskState.get_name(self._state)
        dbg += ' Children: %s' % len(self.children)
        if recursive:
            for child in self.children:
                dbg += '\n' + child.get_dump(indent + 1)
        return dbg

    def dump(self, indent=0):
        """Prints the subtree as a string for debugging."""
        print(self.get_dump())
