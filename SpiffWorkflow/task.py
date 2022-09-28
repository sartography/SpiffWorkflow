# -*- coding: utf-8 -*-

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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

import copy
import logging
import time
import warnings
from uuid import uuid4

from .util.deep_merge import DeepMerge
from .exceptions import WorkflowException

logger = logging.getLogger('spiff')
metrics = logging.getLogger('spiff.metrics')
data_log = logging.getLogger('spiff.data')


def updateDotDict(dct,dotted_path,value):
    parts = dotted_path.split(".")
    path_len = len(parts)
    root = dct
    for i, key in enumerate(parts):
        if (i + 1) < path_len:
            if key not in dct:
                dct[key] = {}
            dct = dct[key]
        else:
            dct[key] = value
    return root


class TaskState:
    """

    The following states may exist:

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
      :class:`Workflow.complete_task_from_id()`.

    - CANCELLED: The task was cancelled by a CancelTask or
      CancelWorkflow task.

    - COMPLETED: The task was regularily completed.

    Note that the LIKELY and MAYBE tasks are merely predicted/guessed, so
    those tasks may be removed from the tree at runtime later. They are
    created to allow for visualizing the workflow at a time where
    the required decisions have not yet been made.
    """
    # Note: The states in this list are ordered in the sequence in which
    # they may appear. Do not change.
    MAYBE = 1
    LIKELY = 2
    FUTURE = 4
    WAITING = 8
    READY = 16
    COMPLETED = 32
    CANCELLED = 64

    FINISHED_MASK = CANCELLED | COMPLETED
    DEFINITE_MASK = FUTURE | WAITING | READY | FINISHED_MASK
    PREDICTED_MASK = FUTURE | LIKELY | MAYBE
    NOT_FINISHED_MASK = PREDICTED_MASK | WAITING | READY
    ANY_MASK = FINISHED_MASK | NOT_FINISHED_MASK


TaskStateNames = {TaskState.FUTURE: 'FUTURE',
                  TaskState.WAITING: 'WAITING',
                  TaskState.READY: 'READY',
                  TaskState.CANCELLED: 'CANCELLED',
                  TaskState.COMPLETED: 'COMPLETED',
                  TaskState.LIKELY: 'LIKELY',
                  TaskState.MAYBE: 'MAYBE'}
TaskStateMasks = {
                  TaskState.FINISHED_MASK: 'FINISHED_MASK',
                  TaskState.DEFINITE_MASK: 'DEFINITE_MASK',
                  TaskState.PREDICTED_MASK: 'PREDICTED_MASK',
                  TaskState.NOT_FINISHED_MASK: 'NOT_FINISHED_MASK',
                  TaskState.ANY_MASK: 'ANY_MASK',
                  }


class DeprecatedMetaTask(type):
    """
    Handle deprecated methods that are now moved to TaskState
    """
    TaskNames = {**TaskStateNames, **TaskStateMasks}
    TaskStateFromNames = {v: k for k, v in TaskNames.items()}

    def __getattribute__(self, item):
        if item in DeprecatedMetaTask.TaskNames.values():
            warnings.warn(f'Task.{item} is deprecated.  '
                          f'Please use TaskState.{item}',
                          DeprecationWarning, stacklevel=2)
            return DeprecatedMetaTask.TaskStateFromNames[item]
        else:
            return type.__getattribute__(self, item)


class Task(object,  metaclass=DeprecatedMetaTask):
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

    See TaskStates for the available states on a Task.
    """

    class Iterator(object):

        MAX_ITERATIONS = 10000

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
            self.count = 1

        def __iter__(self):
            return self

        def _next(self):

            # Make sure that the end is not yet reached.
            if len(self.path) == 0:
                raise StopIteration()

            current = self.path[-1]

            # Assure we don't recurse forever.
            self.count += 1
            if self.count > self.MAX_ITERATIONS:
                raise WorkflowException(current,
                "Task Iterator entered infinite recursion loop" )


            # If the current task has children, the first child is the next
            # item. If the current task is LIKELY, and predicted tasks are not
            # specificly searched, we can ignore the children, because
            # predicted tasks should only have predicted children.
            ignore_task = False
            if self.filter is not None:
                search_predicted = self.filter & TaskState.LIKELY != 0
                is_predicted = current.state & TaskState.LIKELY != 0
                ignore_task = is_predicted and not search_predicted
            if current.children and not ignore_task:
                self.path.append(current.children[0])
                if (self.filter is not None and
                        current.state & self.filter == 0):
                    return None
                return current

            # Ending up here, this task has no children. Crop the path until we
            # reach a task that has unvisited children, or until we hit the
            # end.
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

        def __next__(self):
            # By using this loop we avoid an (expensive) recursive call.
            while True:
                next = self._next()
                if next is not None:
                    return next

        # Python 3 iterator protocol
        next = __next__

    # Pool for assigning a unique thread id to every new Task.
    thread_id_pool = 0

    def __init__(self, workflow, task_spec, parent=None, state=TaskState.MAYBE):
        """
        Constructor.
        """
        assert workflow is not None
        assert task_spec is not None
        self.workflow = workflow
        self.parent = parent
        self.children = []
        self._state = state
        self.triggered = False
        self.task_spec = task_spec
        self.id = uuid4()
        self.thread_id = self.__class__.thread_id_pool
        self.data = {}
        self.terminate_current_loop = False
        self.internal_data = {}
        self.mi_collect_data = {}
        if parent is not None:
            self.parent._child_added_notify(self)

        # TODO: get rid of this stuff
        self.last_state_change = time.time()
        self.state_history = [state]

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value < self._state:
            raise WorkflowException(
                self.task_spec,
                'state went from %s to %s!' % (self.get_state_name(), TaskStateNames[value])
            )
        self._set_state(value)

    def _set_state(self, value):
        """Using the setter method will raise an error on a "backwards" state change.
        Call this method directly to force the state change.
        """
        if value != self.state:
            logger.info(f'State change to {TaskStateNames[value]}', extra=self.log_info())
            self.last_state_change = time.time()
            self.state_history.append(value)
            self._state = value
        else:
            logger.debug(f'State set to {TaskStateNames[value]}', extra=self.log_info())

    def __repr__(self):
        return '<Task object (%s) in state %s at %s>' % (
            self.task_spec.name,
            self.get_state_name(),
            hex(id(self)))

    def log_info(self, dct=None):
        extra = dct or {}
        extra.update({
            'workflow': self.workflow.spec.name,
            'task_spec': self.task_spec.name,
            'task_name': self.task_spec.description,
            'task_id': self.id,
            'task_type': self.task_spec.spec_type,
            'data': self.data if logger.level < 20 else None,
            'internal_data': self.internal_data if logger.level <= 10 else None,
        })
        return extra

    def update_data_var(self, fieldid, value):
        model = {}
        updateDotDict(model,fieldid, value)
        self.update_data(model)

    def update_data(self, data):
        """
        If the task.data needs to be updated from a UserTask form or
        a Script task then use this function rather than updating task.data
        directly.  It will handle deeper merges of data,
        and MultiInstance tasks will be updated correctly.
        """
        self.data = DeepMerge.merge(self.data, data)
        data_log.info('Data update', extra=self.log_info())

    def task_info(self):
        """
        Returns a dictionary of information about the current task, so that
        we can give hints to the user about what kind of task we are working
        with such as a looping task or a Parallel MultiInstance task
        :returns: dictionary
        """
        default = {'is_looping': False,
                   'is_sequential_mi': False,
                   'is_parallel_mi': False,
                   'mi_count': 0,
                   'mi_index': 0}

        miInfo = getattr(self.task_spec, "multiinstance_info", None)
        if callable(miInfo):
            return miInfo(self)
        else:
            return default

    def terminate_loop(self):
        """
        Used in the case that we are working with a BPMN 'loop' task.
        The task will loop, repeatedly asking for input until terminate_loop
        is called on the task
        """
        if self.is_looping():
            self.terminate_current_loop = True
        else:
            raise WorkflowException(self.task_spec,
                                    'The method terminate_loop should only be called in the case of a BPMN Loop Task')

    def is_looping(self):
        """Returns true if this is a looping task."""
        islooping = getattr(self.task_spec, "is_loop_task", None)
        if callable(islooping):
            return self.task_spec.is_loop_task()
        else:
            return False

    def set_children_future(self):
        """
        for a parallel gateway, we need to set up our
        children so that the gateway figures out that it needs to join up
        the inputs - otherwise our child process never gets marked as
        'READY'
        """

        if not self.task_spec.task_should_set_children_future(self):
            return

        self.task_spec.task_will_set_children_future(self)

        # now we set this one to execute

        self._set_state(TaskState.MAYBE)
        self._sync_children(self.task_spec.outputs)
        for child in self.children:
            child.set_children_future()

    def find_children_by_name(self,name):
        """
        for debugging
        """
        return [x for x in self.workflow.task_tree if x.task_spec.name == name]

    def reset_token(self, data, reset_data=False):
        """
        Resets the token to this task. This should allow a trip 'back in time'
        as it were to items that have already been completed.
        :type  reset_data: bool
        :param reset_data: Do we want to have the data be where we left of in
                           this task or not
        """
        self.internal_data = {}
        if not reset_data and self.workflow.last_task and self.workflow.last_task.data:
            # This is a little sly, the data that will get inherited should
            # be from the last completed task, but we don't want to alter
            # the tree, so we just set the parent's data to the given data.
            self.parent.data = copy.deepcopy(data)
        self.workflow.last_task = self.parent
        self.set_children_future()  # this method actually fixes the problem
        self._set_state(TaskState.FUTURE)
        self.task_spec._update(self)

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

    def _drop_children(self, force=False):
        drop = []
        for child in self.children:
            if force or (not child._is_finished()):
                drop.append(child)
            else:
                child._drop_children()
        for task in drop:
            self.children.remove(task)

    def _has_state(self, state):
        """
        Returns True if the Task has the given state flag set.
        """
        return (self.state & state) != 0

    def _is_finished(self):
        return self._has_state(TaskState.FINISHED_MASK)

    def _is_predicted(self):
        return self._has_state(TaskState.PREDICTED_MASK)

    def _is_definite(self):
        return self._has_state(TaskState.DEFINITE_MASK)

    def _add_child(self, task_spec, state=TaskState.MAYBE):
        """
        Adds a new child and assigns the given TaskSpec to it.

        :type  task_spec: TaskSpec
        :param task_spec: The task spec that is assigned to the new child.
        :type  state: integer
        :param state: The bitmask of states for the new child.
        :rtype:  Task
        :returns: The new child task.
        """
        if task_spec is None:
            raise ValueError(self, '_add_child() requires a TaskSpec')
        if self._is_predicted() and state & TaskState.PREDICTED_MASK == 0:
            msg = 'Attempt to add non-predicted child to predicted task'
            raise WorkflowException(self.task_spec, msg)
        task = Task(self.workflow, task_spec, self, state=state)
        task.thread_id = self.thread_id
        if state == TaskState.READY:
            task._ready()
        return task

    def _assign_new_thread_id(self, recursive=True):
        """
        Assigns a new thread id to the task.

        :type  recursive: bool
        :param recursive: Whether to assign the id to children recursively.
        :rtype:  bool
        :returns: The new thread id.
        """
        self.__class__.thread_id_pool += 1
        self.thread_id = self.__class__.thread_id_pool
        if not recursive:
            return self.thread_id
        for child in self:
            child.thread_id = self.thread_id
        return self.thread_id

    def _sync_children(self, task_specs, state=TaskState.MAYBE):
        """
        This method syncs up the task's children with the given list of task
        specs. In other words::

            - Add one child for each given TaskSpec, unless that child already
              exists.
            - Remove all children for which there is no spec in the given list,
              unless it is a "triggered" task.
            - Handle looping back to previous tasks, so we don't end up with
              an infinitely large tree.
        .. note::

           It is an error if the task has a non-predicted child that is
           not given in the TaskSpecs.

        :type  task_specs: list(TaskSpec)
        :param task_specs: The list of task specs that may become children.
        :type  state: integer
        :param state: The bitmask of states for the new children.
        """
        if task_specs is None:
            raise ValueError('"task_specs" argument is None')
        add = task_specs[:]

        # If a child task_spec is also an ancestor, we are looping back,
        # replace those specs with a loopReset task.
        root_task = self._get_root()
        for index, task_spec in enumerate(add):
            ancestor_task = self._find_ancestor(task_spec)
            if ancestor_task and ancestor_task != root_task:
                destination = ancestor_task
                new_spec = self.workflow.get_reset_task_spec(destination)
                new_spec.outputs = []
                new_spec.inputs = task_spec.inputs
                add[index] = new_spec

        # Create a list of all children that are no longer needed.
        remove = []
        for child in self.children:
            # Triggered tasks are never removed.
            if child.triggered:
                continue

            # Check whether the task needs to be removed.
            if child.task_spec in add:
                add.remove(child.task_spec)
                continue

            # Non-predicted tasks must not be removed, so they HAVE to be in
            # the given task spec list.
            if child._is_definite():
                raise WorkflowException(self.task_spec,
                                        'removal of non-predicted child %s' %
                                        repr(child))
            remove.append(child)



        # Remove and add the children accordingly.
        for child in remove:
            self.children.remove(child)
        for task_spec in add:
            self._add_child(task_spec, state)

    def _set_likely_task(self, task_specs):
        if not isinstance(task_specs, list):
            task_specs = [task_specs]
        for task_spec in task_specs:
            for child in self.children:
                if child.task_spec != task_spec:
                    continue
                if child._is_definite():
                    continue
                child._set_state(TaskState.LIKELY)
                return

    def _is_descendant_of(self, parent):
        """
        Returns True if parent is in the list of ancestors, returns False
        otherwise.

        :type  parent: Task
        :param parent: The parent that is searched in the ancestors.
        :rtype:  bool
        :returns: Whether the parent was found.
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

        :type  parent_task_spec: TaskSpec
        :param parent_task_spec: The wanted ancestor.
        :rtype:  Task
        :returns: The child of the given ancestor.
        """
        if self.parent is None:
            return self
        if self.parent.task_spec == parent_task_spec:
            return self
        return self.parent._find_child_of(parent_task_spec)

    def _find_any(self, task_spec):
        """
        Returns any descendants that have the given task spec assigned.

        :type  task_spec: TaskSpec
        :param task_spec: The wanted task spec.
        :rtype:  list(Task)
        :returns: The tasks objects that are attached to the given task spec.
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

        :type  task_spec: TaskSpec
        :param task_spec: The wanted task spec.
        :rtype:  Task
        :returns: The ancestor.
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

        :type  name: str
        :param name: The name of the wanted task.
        :rtype:  Task
        :returns: The ancestor.
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
        if self._has_state(TaskState.COMPLETED) or self._has_state(TaskState.CANCELLED):
            return
        self._set_state(TaskState.READY)
        self.task_spec._on_ready(self)

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
        for state, name in list(TaskStateNames.items()):
            if self._has_state(state):
                state_name.append(name)
        return '|'.join(state_name)

    def get_spec_data(self, name=None, default=None):
        """
        Returns the value of the spec data with the given name, or the given
        default value if the spec data does not exist.

        :type  name: str
        :param name: The name of the spec data field.
        :type  default: obj
        :param default: Return this value if the spec data does not exist.
        :rtype:  obj
        :returns: The value of the spec data.
        """
        return self.task_spec.get_data(name, default)

    def _set_internal_data(self, **kwargs):
        """
        Defines the given attribute/value pairs.
        """
        self.internal_data.update(kwargs)

    def _get_internal_data(self, name, default=None):
        return self.internal_data.get(name, default)

    def set_data(self, **kwargs):
        """
        Defines the given attribute/value pairs.
        """
        self.data.update(kwargs)
        data_log.info('Set data', extra=self.log_info())

    def _inherit_data(self):
        """
        Inherits the data from the parent.
        """
        self.set_data(**self.parent.data)

    def get_data(self, name, default=None):
        """
        Returns the value of the data field with the given name, or the given
        default value if the data field does not exist.

        :type  name: str
        :param name: A data field name.
        :type  default: obj
        :param default: Return this value if the data field does not exist.
        :rtype:  obj
        :returns: The value of the data field
        """
        return self.data.get(name, default)

    def cancel(self):
        """
        Cancels the item if it was not yet completed, and removes
        any children that are LIKELY.
        """
        if self._is_finished():
            for child in self.children:
                child.cancel()
            return
        self._set_state(TaskState.CANCELLED)
        self._drop_children()
        self.task_spec._on_cancel(self)

    def complete(self):
        """
        Called by the associated task to let us know that its state
        has changed (e.g. from FUTURE to COMPLETED.)
        """
        self._set_state(TaskState.COMPLETED)
        # WHY on earth do we mark the task completed and THEN attempt to execute it.
        # A sane model would have success and failure states and instead we return
        # a boolean, with no systematic way of dealing with failures.  This is just
        # crazy!
        start = time.time()
        retval = self.task_spec._on_complete(self)
        extra = self.log_info({
            'action': 'Complete',
            'elapsed': time.time() - start
        })
        metrics.debug('', extra=extra)
        return retval

    def trigger(self, *args):
        """
        If recursive is True, the state is applied to the tree recursively.
        """
        self.task_spec._on_trigger(self, *args)

    def get_dump(self, indent=0, recursive=True):
        """
        Returns the subtree as a string for debugging.

        :rtype:  str
        :returns: The debug information.
        """
        dbg = (' ' * indent * 2)
        dbg += '%s/' % self.id
        dbg += '%s:' % self.thread_id
        dbg += ' Task of %s' % self.get_name()
        if self.task_spec.description:
            dbg += ' (%s)' % self.get_description()
        dbg += ' State: %s' % self.get_state_name()
        dbg += ' Children: %s' % len(self.children)
        if recursive:
            for child in self.children:
                dbg += '\n' + child.get_dump(indent + 1)
        return dbg

    def dump(self, indent=0):
        """
        Prints the subtree as a string for debugging.
        """
        print(self.get_dump())
