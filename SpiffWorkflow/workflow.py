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

import logging

from .task import Task, TaskState, TaskIterator, TaskFilter
from .util.compat import mutex
from .util.event import Event
from .exceptions import TaskNotFoundException, WorkflowException

logger = logging.getLogger('spiff')


class Workflow(object):
    """
    The engine that executes a workflow.
    It is a essentially a facility for managing all branches.
    A Workflow is also the place that holds the data of a running workflow.
    """

    def __init__(self, workflow_spec, deserializing=False):
        """
        Constructor.

        :type workflow_spec: specs.WorkflowSpec
        :param workflow_spec: The workflow specification.
        :type deserializing: bool
        :param deserializing: set to true when deserializing to avoid
          generating tasks twice (and associated problems with multiple
          hierarchies of tasks)
        """
        assert workflow_spec is not None
        self.spec = workflow_spec
        self.data = {}
        self.locks = {}
        self.last_task = None
        self.success = True
        self.tasks = {}

        # Events.
        self.completed_event = Event()

        if not deserializing:
            self.task_tree = Task(self, self.spec.start, state=TaskState.FUTURE)
            self.task_tree.task_spec._predict(self.task_tree, mask=TaskState.NOT_FINISHED_MASK)
            self.task_tree._ready()
            logger.info('Initialize', extra=self.log_info())

    def log_info(self, dct=None):
        extra = dct or {}
        extra.update({
            'workflow_spec': self.spec.name,
            'task_spec': '-',
            'task_type': None,
            'task_id': None,
            'data': None,
        })
        return extra

    def is_completed(self):
        """Checks whether the workflow is complete.

        Returns:
            bool: True if the workflow has no unfinished tasks
        """
        iter = TaskIterator(self.task_tree, task_filter=TaskFilter(state=TaskState.NOT_FINISHED_MASK))
        try:
            next(iter)
        except StopIteration:
            # No waiting tasks found.
            return True
        return False

    def manual_input_required(self):
        """Checks whether the workflow requires manual input.

        Returns:
            bool: True if the workflow cannot proceed until manual tasks are complete
        """
        iter = TaskIterator(self.task_tree, task_filter=TaskFilter(state=TaskState.READY, manual=False))
        try:
            next(iter)
        except StopIteration:
            return True
        return False

    def _predict(self, mask=TaskState.NOT_FINISHED_MASK):
        for task in Workflow.get_tasks(self, task_filter=TaskFilter(state=TaskState.NOT_FINISHED_MASK)):
            task.task_spec._predict(task, mask=mask)

    def _task_completed_notify(self, task):
        if task.get_name() == 'End':
            self.data.update(task.data)
        self.update_waiting_tasks()
        if self.completed_event.n_subscribers() > 0 and self.is_completed():
            # Since is_completed() is expensive it makes sense to bail out if calling it is not necessary.
            self.completed_event(self)

    def _get_mutex(self, name):
        if name not in self.locks:
            self.locks[name] = mutex()
        return self.locks[name]

    def get_task_mapping(self):
        task_mapping = {}
        for task in self.task_tree:
            thread_task_mapping = task_mapping.get(task.thread_id, {})
            tasks = thread_task_mapping.get(task.task_spec, set())
            tasks.add(task)
            thread_task_mapping[task.task_spec] = tasks
            task_mapping[task.thread_id] = thread_task_mapping
        return task_mapping

    def set_data(self, **kwargs):
        """Defines the given attribute/value pairs."""
        self.data.update(kwargs)

    def get_data(self, name, default=None):
        """
        Returns the value of the data field with the given name, or the given
        default value if the data field does not exist.

        :type  name: str
        :param name: A data field name.
        :type  default: obj
        :param default: Return this value if the data field does not exist.
        :rtype:  obj
        :returns: The value of the data field.
        """
        return self.data.get(name, default)

    def cancel(self, success=False):
        """
        Cancels all open tasks in the workflow.

        :type  success: bool
        :param success: Whether the Workflow should be marked as successfully completed.
        """
        self.success = success
        cancel = []
        for task in self.task_tree:
            cancel.append(task)
        for task in cancel:
            task.cancel()
        logger.info(f'Cancel with {len(cancel)} remaining', extra=self.log_info())
        return cancel

    def get_tasks_iterator(self, **kwargs):
        """
        Returns a iterator of Task objects with the given state.

        :rtype:  Task.Iterator
        :returns: A list of tasks.
        """
        return TaskIterator(self.task_tree, **kwargs)

    def get_tasks(self, **kwargs):
        """
        Returns a list of Task objects with the given state.

        :rtype:  list[Task]
        :returns: A list of tasks.
        """
        return [t for t in TaskIterator(self.task_tree, **kwargs)]

    def get_next_task(self, first_task=None, **kwargs):
        """Returns the next task that meets the iteration conditions, starting from the root by default.

        Parameters:
            first_task (Task): search beginning from this task

        Notes:
            Other keyword args are passed directly into `TaskIterator`

        Returns:
            Task or None: the first task that meets the conditions or None if no tasks match        
        """
        iter = TaskIterator(first_task or self.task_tree, **kwargs)
        try:
            return next(iter)
        except StopIteration:
            return None

    def get_task_from_id(self, task_id):
        """
        Returns the task with the given id.

        :type id:integer
        :param id: The id of a task.
        :rtype: Task
        :returns: The task with the given id.
        """
        if task_id is None:
            raise WorkflowException('task_id is None', task_spec=self.spec)
        elif task_id not in self.tasks:
            raise TaskNotFoundException(f'A task with id {task_id} was not found', task_spec=self.spec)
        return self.tasks.get(task_id)

    def run_task_from_id(self, task_id):
        """
        Runs the task with the given id.

        :type  task_id: integer
        :param task_id: The id of the Task object.
        """
        task = self.get_task_from_id(task_id)
        return task.run()

    def reset_from_task_id(self, task_id, data=None):
        """
        Runs the task with the given id.

        :type  task_id: integer
        :param task_id: The id of the Task object.
        :param data: optionall set the task data
        """
        task = self.get_task_from_id(task_id)
        self.last_task = task.parent
        return task.reset_token(data)

    def run_next(self, use_last_task=True, halt_on_manual=True):
        """Runs the next task, starting from the branch containing the last completed task by default.

        Parameters:
            use_last_task (bool): start with the currently running branch
            halt_on_manual (bool): do not run tasks whose spec's have the `manual` attribute set

        Returns:
            bool: True when a task runs sucessfully
        """
        first_task = self.last_task if use_last_task and self.last_task is not None else self.task_tree
        task_filter = TaskFilter(
            state=TaskState.READY,
            manual=False if halt_on_manual else None,
        )
        task = self.get_next_task(first_task, task_filter=task_filter)
        # If we didn't execute anything on the current branch, retry from the root task
        if task is None and use_last_task:
            task = self.get_next_task(self.task_tree, task_filter=task_filter)

        if task is None:
            # If no task was found, update any waiting tasks
            self.update_waiting_tasks()
        else:
            return task.run()

    def run_all(self, use_last_task=True, halt_on_manual=True):
        """Runs all possible tasks, starting from the current branch by default.

        Parameters:
            use_last_task (bool): start with the currently running branch
            halt_on_manual (bool): do not run tasks whose spec's have the `manual` attribute set
        """
        while self.run_next(use_last_task, halt_on_manual):
            pass

    def update_waiting_tasks(self):
        """Update all tasks in the WAITING state"""

        for task in TaskIterator(self.task_tree, task_filter=TaskFilter(state=TaskState.WAITING)):
            task.task_spec._update(task)

    def get_dump(self):
        """
        Returns a complete dump of the current internal task tree for
        debugging.

        :rtype:  str
        :returns: The debug information.
        """
        return self.task_tree.get_dump()

    def dump(self):
        """
        Like :meth:`get_dump`, but prints the output to the terminal instead
        of returning it.
        """
        print(self.task_tree.dump())

    def serialize(self, serializer, **kwargs):
        """
        Serializes a Workflow instance using the provided serializer.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :type  kwargs: dict
        :param kwargs: Passed to the serializer.
        :rtype:  object
        :returns: The serialized workflow.
        """
        return serializer.serialize_workflow(self, **kwargs)

    @classmethod
    def deserialize(cls, serializer, s_state, **kwargs):
        """
        Deserializes a Workflow instance using the provided serializer.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :type  s_state: object
        :param s_state: The serialized workflow.
        :type  kwargs: dict
        :param kwargs: Passed to the serializer.
        :rtype:  Workflow
        :returns: The workflow instance.
        """
        return serializer.deserialize_workflow(s_state, **kwargs)
