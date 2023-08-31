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


class TaskState:
    """Int values corresponding to `Task` states.
    
    The following states may exist:

    - LIKELY: The task is a descendant of the default branch of a Choice task.

    - MAYBE: The task is a descendant of a conditional branch of a Choice task.

    - FUTURE: The task will definitely be reached in the future, regardless of
      which choices the user makes within the workflow.

    - WAITING: The task has been reached but the conditions for running this
      task have not been met. For example, a Join task will be WAITING until
      all predecessors are completed.

    - READY: The conditions for running the task are now satisfied.  All
      predecessors have completed and the task may now be run using `Task.run`.

    - STARTED: `Task.run` has been called, but the task returned
      before finishing.  SpiffWorkflow does not track tasks in this state, as
      it is currently unused by any of the included task specs.

    - COMPLETED: The task was regularily completed.

    - ERROR: The task did not complete because an error occurred when it was run.

    - CANCELLED: The task was cancelled.

    Notes:
    
        - LIKELY and MAYBE tasks are merely predicted/guessed, so those tasks may be
          removed from the tree at runtime later.

        - The STARTED state will eventually be used by SpiffWorkflow.   The intention
          is that this state would be used if a time-consuming and/or resource intensive
          operation was being carried out external to the workflow.  The task could
          return immediately and its branch would not proceed until the workflow application
          called `Task.complete`, but without blocking other branches that were ready to
          execute.
    """
    MAYBE = 1
    LIKELY = 2
    FUTURE = 4
    WAITING = 8
    READY = 16
    STARTED = 32
    COMPLETED = 64
    ERROR = 128
    CANCELLED = 256

    FINISHED_MASK = CANCELLED | ERROR | COMPLETED
    DEFINITE_MASK = FUTURE | WAITING | READY | STARTED
    PREDICTED_MASK = LIKELY | MAYBE
    NOT_FINISHED_MASK = PREDICTED_MASK | DEFINITE_MASK
    ANY_MASK = FINISHED_MASK | NOT_FINISHED_MASK

    _names = ['MAYBE', 'LIKELY', 'FUTURE', 'WAITING', 'READY', 'STARTED', 'COMPLETED', 'ERROR', 'CANCELLED']
    _values = [1, 2, 4, 8, 16, 32, 64, 128, 256]

    @classmethod
    def get_name(cls, state):
        """Get the name of the state or mask from the value.

        Args:
            state (int): a `TaskState` value
        
        Returns:
            str: the name of the state
        """
        names = dict(zip(cls._values, cls._names))
        names.update({
            TaskState.FINISHED_MASK: 'FINISHED_MASK',
            TaskState.DEFINITE_MASK: 'DEFINITE_MASK',
            TaskState.PREDICTED_MASK: 'PREDICTED_MASK',
            TaskState.NOT_FINISHED_MASK: 'NOT_FINISHED_MASK',
            TaskState.ANY_MASK: 'ANY_MASK',
        })
        return names.get(state)

    @classmethod
    def get_value(cls, name):
        """Get the value for the state name (case insensitive).

        Args:
            name (str): the state name

        Returns:
            int: the value of the state
        """
        values = dict(zip(cls._names, cls._values))
        return values.get(name.upper())

 
class TaskFilter:
    """This is the default class for filtering during task iteration.

    Note:
        All filter values must match.  Default filter values match any task.
    """

    def __init__(self, state=TaskState.ANY_MASK, updated_ts=0, manual=None, spec_name=None, spec_class=None):
        """
        Parameters:
            state (`TaskState`):      limit results to state or mask
            updated_ts (float):     limit results to tasks updated at or after this timestamp
            manual (bool):          match the value of the `TaskSpec`'s manual attribute
            spec_name (str):        match the value of the `TaskSpec`'s name
            spec_class (`TaskSpec`):   match the value of the `TaskSpec`'s class
        """
        self.state = state
        self.updated_ts = updated_ts
        self.manual = manual
        self.spec_name = spec_name
        self.spec_class = spec_class

    def matches(self, task):
        """Check if the task matches this filter.

        Args:
            task (`Task`): the task to check

        Returns:
            bool: indicates whether the task matches
        """
        return all([
            task.has_state(self.state),
            task.last_state_change >= self.updated_ts,
            self.manual is None or task.task_spec.manual == self.manual,
            self.spec_name is None or task.task_spec.name == self.spec_name,
            self.spec_class is None or isinstance(task.task_spec, self.spec_class),
        ])


class TaskIterator:
    """Default task iteration class."""

    def __init__(self, task, end_at_spec=None, max_depth=1000, depth_first=True, task_filter=None, **kwargs):
        """Iterate over the task tree and return the tasks matching the filter parameters.

        Args:
            task (`Task`):    the task to start from

        Keyword Args:
            end_at (str):stop when a task spec with this name is reached
            max_depth (int): stop when this depth is reached
            depth_first (bool): return results in depth first order
            task_filter (`TaskFilter`): return only tasks matching this filter
        
        Notes:
            Keyword args not used by this class will be passed into `TaskFilter` if no `task_filter` is provided.
            This is for convenience (filter values can be used directly from `Workflow.get_tasks`) as well as
            backwards compatilibity for queries about `TaskState`.
        """
        self.task_filter = task_filter or TaskFilter(**kwargs)
        self.end_at_spec = end_at_spec
        self.max_depth = max_depth
        self.depth_first = depth_first

        self.task_list = [task]
        self.depth = 0
        # Figure out which states need to be traversed.
        # Predicted tasks can follow definite tasks but not vice versa; definite tasks can follow finished tasks but not vice versa
        # The dream is for a child task to always have a lower task state than its parent; currently we have parents that wait for
        # their children
        if self.task_filter.state & TaskState.PREDICTED_MASK:
            self.min_state = TaskState.MAYBE
        elif self.task_filter.state & TaskState.DEFINITE_MASK:
            self.min_state = TaskState.FUTURE
        else:
            self.min_state = TaskState.COMPLETED

    def __iter__(self):
        return self

    def __next__(self):
        task = self._next()
        while not self.task_filter.matches(task):
            task = self._next()
        return task

    def _next(self):

        if len(self.task_list) == 0:
            raise StopIteration()

        task = self.task_list.pop(-1)
        if all([
            len(task._children) > 0,
            task.state >= self.min_state,
            self.depth < self.max_depth,
            task.task_spec.name != self.end_at_spec,
        ]):
            if self.depth_first:
                self.task_list.extend(reversed(task.children))
            else:
                self.task_list = reversed(task.children) + self.task_list
            self.depth += 1
        elif len(self.task_list) > 0 and task.parent != self.task_list[0].parent:
            self.depth -= 1
        return task

