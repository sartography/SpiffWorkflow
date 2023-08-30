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
        values = dict(zip(cls._names, cls._values))
        return values.get(name)

 
class TaskFilter:

    def __init__(self, state=TaskState.ANY_MASK, updated_after=0, manual=None, spec_name=None, spec_class=None):
        """
        Parameters:
            state (TaskState): limit results to state or mask
            updated_after (float): limit results to tasks updated after this timestamp
            manual (bool): match the value of the task's spec's manual attribute
            spec_name (str): match the value of the task's spec's name
            spec_class (TaskSpec): match the value of the task's spec's class

        Notes:
            If no parameter value is provided, all tasks will match
        """
        self.state = state
        self.updated_after = updated_after
        self.manual = manual
        self.spec_name = spec_name
        self.spec_class = spec_class

    def matches(self, task):
        """Check if the task matches this filter

        Args:
            task (Task): the task to check

        Returns:
            bool: indicates whether the task matches
        """
        return all([
            task._has_state(self.state),
            task.last_state_change > self.updated_after,
            self.manual is None or task.task_spec.manual == self.manual,
            self.spec_name is None or task.task_spec.name == self.spec_name,
            self.spec_class is None or isinstance(task.task_spec, self.spec_class),
        ])


class TaskIterator:

    def __init__(self, task, end_at_spec=None, max_depth=1000, depth_first=True, task_filter=None, **kwargs):
        """Iterate over the task tree and return the tasks matching the filter parameters.

        Args:
            task (Task): the task to start from

        Keyword Args:
            end_at (str): stop when a task spec with this name is reached
            max_depth (int): stop when this depth is reached
            depth_first (bool): return results in depth first order
            task_filter (TaskFilter): return only tasks matching this filter
        
        Notes:
            Remaining keyword args will be passed into the default `TaskFilter` class if no `task_filter` is provided.
        """
        self.task_filter = task_filter or TaskFilter(**kwargs)
        self.end_at_spec = end_at_spec
        self.max_depth = max_depth
        self.depth_first = depth_first

        self.queue = [task]
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

        if len(self.queue) == 0:
            raise StopIteration()

        task = self.queue.pop(-1)
        if all([
            len(task._children) > 0,
            task.state >= self.min_state,
            self.depth < self.max_depth,
            task.task_spec.name != self.end_at_spec,
        ]):
            if self.depth_first:
                self.queue.extend(reversed(task.children))
            else:
                self.queue = reversed(task.children) + self.queue
            self.depth += 1
        elif len(self.queue) > 0 and task.parent != self.queue[0].parent:
            self.depth -= 1
        return task

