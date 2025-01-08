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
from typing import Optional, Any

from .serializer.base import Serializer
from .specs import WorkflowSpec
from .task import Task
from .util.task import TaskState, TaskIterator, TaskFilter
from .util.compat import mutex
from .util.event import Event
from .exceptions import TaskNotFoundException

logger = logging.getLogger('spiff.workflow')


class Workflow:
    """The instantiation of a `WorkflowSpec`.

    Represents the state of a running workflow and its data.

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

    def __init__(
        self,
        workflow_spec: WorkflowSpec,
        deserializing: bool = False,
    ) -> None:
        """
        Parameters:
            workflow_spec: The spec that describes this workflow.
            deserializing: Whether this workflow is being deserialized.
        """
        self.spec = workflow_spec
        self.data = {}
        self.locks = {}
        self.last_task = None
        self.success = True
        self.tasks = {}
        self.completed = False

        # Events.
        self.completed_event = Event()

        if not deserializing:
            self.task_tree = Task(self, self.spec.start, state=TaskState.FUTURE)
            self.task_tree.task_spec._predict(self.task_tree, mask=TaskState.NOT_FINISHED_MASK)
            logger.info('Initialized workflow', extra=self.collect_log_extras())
            self.task_tree._ready()

    def is_completed(self) -> bool:
        """Checks whether the workflow is complete.

        Returns:
            True if the workflow has no unfinished tasks.
        """
        if not self.completed:
            _iter = TaskIterator(self.task_tree, state=TaskState.NOT_FINISHED_MASK)
            try:
                next(_iter)
            except StopIteration:
                self.completed = True
        return self.completed

    def manual_input_required(self) -> bool:
        """Checks whether the workflow requires manual input.

        Returns:
            True if the workflow cannot proceed until manual tasks are complete.
        """
        _iter = TaskIterator(self.task_tree, state=TaskState.READY, manual=False)
        try:
            next(_iter)
        except StopIteration:
            return True
        return False

    def get_tasks(self, first_task: Task = None, **kwargs) -> list[Task]:
        """Returns a list of `Task`s that meet the conditions specified `kwargs`, starting from the root by default.

        Notes:
            Keyword args are passed directly to `get_tasks_iterator`.

        Returns:
            The tasks that match the filtering conditions.
        """
        return [task for task in self.get_tasks_iterator(first_task, **kwargs)]

    def get_next_task(self, first_task: Task = None, **kwargs) -> Optional[Task]:
        """Returns the next task that meets the iteration conditions, starting from the root by default.

        Parameters:
            first_task: Search beginning from this task.

        Notes:
            Other keyword args are passed directly into `get_tasks_iterator`.

        Returns:
            The first task that meets the conditions or None if no tasks match
        """
        _iter = self.get_tasks_iterator(first_task, **kwargs)
        try:
            return next(_iter)
        except StopIteration:
            return None

    def get_tasks_iterator(self, first_task: Task = None, **kwargs) -> TaskIterator:
        """Returns an iterator of Tasks that meet the conditions specified `kwargs`, starting from the root by default.

        Parameters:
            first_task: Search beginning from this task.

        Notes:
            Other keyword args are passed directly into `TaskIterator`.

        Returns:
            An iterator over the matching tasks.
        """
        return TaskIterator(first_task or self.task_tree, **kwargs)

    def get_task_from_id(self, task_id: str) -> Task:
        """Returns the task with the given id.

        Args:
            task_id: The id of the task to run.

        Returns:
            The task.

        Raises:
            `TaskNotFoundException`: if the task does not exist
        """
        if task_id not in self.tasks:
            raise TaskNotFoundException(f'A task with id {task_id} was not found', task_spec=self.spec)
        return self.tasks.get(task_id)

    def run_task_from_id(self, task_id: str) -> Optional[bool]:
        """Runs the task with the given id.

        Args:
            task_id: The id of the task to run.
        """
        task = self.get_task_from_id(task_id)
        return task.run()

    def run_next(self, use_last_task: bool = True, halt_on_manual: bool = True) -> bool:
        """Runs the next task, starting from the branch containing the last completed task by default.

        Parameters:
            use_last_task: Start with the currently running branch.
            halt_on_manual: Do not run tasks with `TaskSpec`s that have the `manual` attribute set.

        Returns:
            True when a task runs successfully.
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

    def run_all(self, use_last_task: bool = True, halt_on_manual: bool = True) -> None:
        """Runs all possible tasks, starting from the current branch by default.

        Parameters:
            use_last_task: Start with the currently running branch.
            halt_on_manual: Do not run tasks with `TaskSpec`s that have the `manual` attribute set.
        """
        while self.run_next(use_last_task, halt_on_manual):
            pass

    def update_waiting_tasks(self) -> None:
        """Update all tasks in the WAITING state"""
        for task in TaskIterator(self.task_tree, state=TaskState.WAITING):
            task.task_spec._update(task)

    def cancel(self, success: bool = False) -> list[Task]:
        """Cancels all open tasks in the workflow.

        Args:
            success: The state of the workflow.

        Returns:
            The cancelled tasks.
        """
        self.success = success
        self.completed = True
        logger.info(f'Workflow cancelled', extra=self.collect_log_extras())
        cancelled = []
        for task in TaskIterator(self.task_tree, state=TaskState.NOT_FINISHED_MASK):
            cancelled.append(task)
        for task in cancelled:
            task.cancel()
        return cancelled

    def set_data(self, **kwargs) -> None:
        """Defines the given attribute/value pairs."""
        self.data.update(kwargs)

    def get_data(self, name: str, default: Optional[Any] = None) -> Optional[Any]:
        """Returns the value of the data field with the given name, or the given
        default value if the data field does not exist.

        Args:
            name: The dictionary key to return.
            default: A default value to return if the key does not exist.

        Returns:
            The value of the key, or the default.
        """
        return self.data.get(name, default)

    def reset_from_task_id(self, task_id: str, data: dict = None) -> list[Task]:
        """Removed all descendants of this task and set this task to be runnable.

        Args:
            task_id: The id of the task to reset to.
            data: Optionally replace the data (if None, data will be copied from the parent task).

        Returns:
            Tasks removed from the tree.
        """
        task = self.get_task_from_id(task_id)
        self.last_task = task.parent
        return task.reset_branch(data)

    def collect_log_extras(self, dct: Optional[dict] = None) -> dict:
        """Return logging details for this workflow."""
        extra = dct or {}
        extra.update({
            'workflow_spec': self.spec.name,
            'success': self.success,
            'completed': self.completed,
        })
        if logger.level < 20:
            extra.update({'tasks': [t.id for t in Workflow.get_tasks(self)]})
        return extra

    def _predict(self, mask: TaskState = TaskState.NOT_FINISHED_MASK) -> None:
        """Predict tasks with the provided mask."""
        for task in Workflow.get_tasks(self, state=TaskState.NOT_FINISHED_MASK):
            task.task_spec._predict(task, mask=mask)

    def _task_completed_notify(self, task: Task) -> None:
        """Called whenever a task completes."""
        self.last_task = task
        if task.task_spec.name == 'End':
            self._mark_complete(task)
        if self.completed:
            self.completed_event(self)
        else:
            self.update_waiting_tasks()

    def _remove_task(self, task_id: str) -> None:
        task = self.tasks[task_id]
        for child in task.children:
            self._remove_task(child.id)
        task.parent._children.remove(task.id)
        self.tasks.pop(task_id)

    def _mark_complete(self, task: Task) -> None:
        logger.info('Workflow completed', extra=self.collect_log_extras())
        self.data.update(task.data)
        self.completed = True

    def _get_mutex(self, name: str) -> mutex:
        """Get or create a mutex."""
        if name not in self.locks:
            self.locks[name] = mutex()
        return self.locks[name]

    def get_task_mapping(self) -> dict:
        """I don't know that this does.

        Seriously, this returns a mapping of thread ids to tasks in that thread.  It can be used to identify
        tasks by branch and use this information for decision-making (despite the flawed implementation
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

    def get_dump(self) -> str:
        """Returns a string representation of the task tree.

        Returns:
            A tree view of the current workflow state.
        """
        return self.task_tree.get_dump()

    def dump(self) -> None:
        """Print a dump of the current task tree."""
        print(self.task_tree.dump())

    def serialize(self, serializer: Serializer, **kwargs) -> Any:
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
    def deserialize(cls, serializer: Serializer, s_state: Any, **kwargs) -> "Workflow":
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
