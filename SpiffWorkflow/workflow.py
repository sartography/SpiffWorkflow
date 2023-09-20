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

from .task import Task
from .util.task import TaskState, TaskIterator, TaskFilter
from .util.compat import mutex
from .util.event import Event
from .exceptions import TaskNotFoundException, WorkflowException

logger = logging.getLogger('spiff')


class Workflow(object):
    """The instantiation of a `WorkflowSpec`.

    Reprsents the state of a running workflow and its data.

    Attributes:
        spec (`WorkflowSpec`): the spec that describes this workflow instance
        data (dict): the data associated with the workflow
        locks (dict): a dictionary holding locaks used by Mutex tasks
        last_task (`Task`): the last successfully completed task
        success (bool): whether the workflow was successful
        tasks (dict(id, `Task`)): a mapping of task ids to tasks
        task_tree (`Task`): the root task of this workflow's task tree
        completed_event (`Event`): an event holding callbacks to be run when the workflow completes
    """

    def __init__(self, workflow_spec, deserializing=False):
        """
        Parameters:
            workflow_spec (`WorkflowSpec`): the spec that describes this workflow
            deserializing (bool): whether this workflow is being deserialized
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

    def is_completed(self):
        """Checks whether the workflow is complete.

        Returns:
            bool: True if the workflow has no unfinished tasks
        """
        iter = TaskIterator(self.task_tree, state=TaskState.NOT_FINISHED_MASK)
        try:
            next(iter)
        except StopIteration:
            return True
        return False

    def manual_input_required(self):
        """Checks whether the workflow requires manual input.

        Returns:
            bool: True if the workflow cannot proceed until manual tasks are complete
        """
        iter = TaskIterator(self.task_tree, state=TaskState.READY, manual=False)
        try:
            next(iter)
        except StopIteration:
            return True
        return False

    def get_tasks(self, first_task=None, **kwargs):
        """Returns a list of `Task`s that meet the conditions specified `kwargs`, starting from the root by default.

        Notes:
            Keyword args are passed directly to `get_tasks_iterator`

        Returns:
            list(`Task`): the tasks that match the filtering conditions
        """
        return [t for t in self.get_tasks_iterator(first_task, **kwargs)]

    def get_next_task(self, first_task=None, **kwargs):
        """Returns the next task that meets the iteration conditions, starting from the root by default.

        Parameters:
            first_task (`Task`): search beginning from this task

        Notes:
            Other keyword args are passed directly into `get_tasks_iterator`

        Returns:
            `Task` or None: the first task that meets the conditions or None if no tasks match        
        """
        iter = self.get_tasks_iterator(first_task, **kwargs)
        try:
            return next(iter)
        except StopIteration:
            return None

    def get_tasks_iterator(self, first_task=None, **kwargs):
        """Returns an iterator of Tasks that meet the conditions specified `kwargs`, starting from the root by default.

        Parameters:
            first_task (`Task`): search beginning from this task

        Notes:
            Other keyword args are passed directly into `TaskIterator`        

        Returns:
            `TaskIterator`: an iterator over the matching tasks
        """
        return TaskIterator(first_task or self.task_tree, **kwargs)

    def get_task_from_id(self, task_id):
        """Returns the task with the given id.

        Args:
            task_id: the id of the task to run

        Returns:
            `Task`: the task

        Raises:
            `TaskNotFoundException`: if the task does not exist
        """
        if task_id not in self.tasks:
            raise TaskNotFoundException(f'A task with id {task_id} was not found', task_spec=self.spec)
        return self.tasks.get(task_id)

    def run_task_from_id(self, task_id):
        """Runs the task with the given id.

        Args:
            task_id: the id of the task to run
        """
        task = self.get_task_from_id(task_id)
        return task.run()

    def run_next(self, use_last_task=True, halt_on_manual=True):
        """Runs the next task, starting from the branch containing the last completed task by default.

        Parameters:
            use_last_task (bool): start with the currently running branch
            halt_on_manual (bool): do not run tasks with `TaskSpec`s that have the `manual` attribute set

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
            # If no task was found, update any waiting tasks.  Ideally, we wouldn't do this, but currently necessary.
            self.update_waiting_tasks()
        else:
            return task.run()

    def run_all(self, use_last_task=True, halt_on_manual=True):
        """Runs all possible tasks, starting from the current branch by default.

        Parameters:
            use_last_task (bool): start with the currently running branch
            halt_on_manual (bool): do not run tasks with `TaskSpec`s that have the `manual` attribute set
        """
        while self.run_next(use_last_task, halt_on_manual):
            pass

    def update_waiting_tasks(self):
        """Update all tasks in the WAITING state"""
        for task in TaskIterator(self.task_tree, state=TaskState.WAITING):
            task.task_spec._update(task)

    def cancel(self, success=False):
        """Cancels all open tasks in the workflow.

        Args:
            success (bool): the state of the workflow

        Returns:
            list(`Task`): the cancelled tasks
        """
        self.success = success
        cancel = []
        for task in TaskIterator(self.task_tree, state=TaskState.NOT_FINISHED_MASK):
            cancel.append(task)
        for task in cancel:
            task.cancel()
        logger.info(f'Cancel with {len(cancel)} remaining', extra=self.log_info())
        return cancel

    def set_data(self, **kwargs):
        """Defines the given attribute/value pairs."""
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

    def reset_from_task_id(self, task_id, data=None):
        """Removed all descendendants of this task and set this task to be runnable.

        Args:
            task_id: the id of the task to reset to
            data (dict): optionally replace the data (if None, data will be copied from the parent task)

        Returns:
            list(`Task`): tasks removed from the tree
        """
        task = self.get_task_from_id(task_id)
        self.last_task = task.parent
        return task.reset_branch(data)

    def log_info(self, dct=None):
        """Return logging details for this workflow"""
        extra = dct or {}
        extra.update({
            'workflow_spec': self.spec.name,
            'task_spec': None,
            'task_type': None,
            'task_id': None,
            'data': None,
        })
        return extra

    def _predict(self, mask=TaskState.NOT_FINISHED_MASK):
        """Predict tasks with the provided mask"""
        for task in Workflow.get_tasks(self, state=TaskState.NOT_FINISHED_MASK):
            task.task_spec._predict(task, mask=mask)

    def _task_completed_notify(self, task):
        """Called whenever a task completes"""
        if task.task_spec.name == 'End':
            self.data.update(task.data)
        self.update_waiting_tasks()
        if self.completed_event.n_subscribers() > 0 and self.is_completed():
            # Since is_completed() is expensive it makes sense to bail out if calling it is not necessary.
            self.completed_event(self)

    def _get_mutex(self, name):
        """Get or create a mutex"""
        if name not in self.locks:
            self.locks[name] = mutex()
        return self.locks[name]

    def get_task_mapping(self):
        """I don't know that this does.

        Seriously, this returns a mapping of thread ids to tasks in that thread.  It can be used to identify
        tasks by branch and use this information for decision making (despite the flawed implementation
        mechanism; IMO, this should be maintained by the workflow rather than a class attribute).
        """
        task_mapping = {}
        for task in self.task_tree:
            thread_task_mapping = task_mapping.get(task.thread_id, {})
            tasks = thread_task_mapping.get(task.task_spec, set())
            tasks.add(task)
            thread_task_mapping[task.task_spec] = tasks
            task_mapping[task.thread_id] = thread_task_mapping
        return task_mapping

    def get_dump(self):
        """Returns a string representation of the task tree.

        Returns:
            str: a tree view of the current workflow state
        """
        return self.task_tree.get_dump()

    def dump(self):
        """Print a dump of the current task tree"""
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
