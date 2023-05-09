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

from .specs.Simple import Simple
from .task import Task, TaskState
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

    def __init__(self, workflow_spec, deserializing=False, **kwargs):
        """
        Constructor.

        :type workflow_spec: specs.WorkflowSpec
        :param workflow_spec: The workflow specification.
        :type deserializing: bool
        :param deserializing: set to true when deserializing to avoid
          generating tasks twice (and associated problems with multiple
          hierarchies of tasks)
        """
        self.name = None
        assert workflow_spec is not None
        self.spec = workflow_spec
        self.data = {}
        self.outer_workflow = kwargs.get('parent', self)
        self.locks = {}
        self.last_task = None
        if 'Root' in workflow_spec.task_specs:
            root = workflow_spec.task_specs['Root']
        else:
            root = Simple(workflow_spec, 'Root')

        # Setting TaskState.COMPLETED prevents the root task from being executed.
        self.task_tree = Task(self, root, state=TaskState.COMPLETED)
        start = self.task_tree._add_child(self.spec.start, state=TaskState.FUTURE)
        self.success = True
        self.debug = False

        # Events.
        self.completed_event = Event()

        if not deserializing:
            self._predict()
            if 'parent' not in kwargs:
                start.task_spec._update(start)
            logger.info('Initialize', extra=self.log_info())

        self.task_mapping = self._get_task_mapping()

    def log_info(self, dct=None):
        extra = dct or {}
        extra.update({
            'workflow_spec': self.spec.name,
            'workflow_name': self.spec.description,
            'task_spec': '-',
            'task_type': None,
            'task_id': None,
            'data': None,
        })
        return extra

    def is_completed(self):
        """
        Returns True if the entire Workflow is completed, False otherwise.

        :rtype: bool
        :return: Whether the workflow is completed.
        """
        mask = TaskState.NOT_FINISHED_MASK
        iter = Task.Iterator(self.task_tree, mask)
        try:
            nexttask = next(iter)
        except StopIteration:
            # No waiting tasks found.
            return True
        return False

    def _predict(self, mask=TaskState.NOT_FINISHED_MASK):
        for task in Workflow.get_tasks(self,TaskState.NOT_FINISHED_MASK):
            task.task_spec._predict(task, mask=mask)

    def _get_waiting_tasks(self):
        waiting = Task.Iterator(self.task_tree, TaskState.WAITING)
        return [w for w in waiting]

    def _task_completed_notify(self, task):
        if task.get_name() == 'End':
            self.data.update(task.data)
        # Update the state of every WAITING task.
        for thetask in self._get_waiting_tasks():
            thetask.task_spec._update(thetask)
        if self.completed_event.n_subscribers() == 0:
            # Since is_completed() is expensive it makes sense to bail
            # out if calling it is not necessary.
            return
        if self.is_completed():
            self.completed_event(self)

    def _get_mutex(self, name):
        if name not in self.locks:
            self.locks[name] = mutex()
        return self.locks[name]

    def _get_task_mapping(self):
        task_mapping = {}
        for task in self.task_tree:
            thread_task_mapping = task_mapping.get(task.thread_id, {})
            tasks = thread_task_mapping.get(task.task_spec, set())
            tasks.add(task)
            thread_task_mapping[task.task_spec] = tasks
            task_mapping[task.thread_id] = thread_task_mapping
        return task_mapping

    def update_task_mapping(self):
        """
        Update the task_mapping of workflow, make sure the method is called
        every time you reconstruct task instance.
        """
        self.task_mapping = self._get_task_mapping()

    def set_data(self, **kwargs):
        """
        Defines the given attribute/value pairs.
        """
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
        :param success: Whether the Workflow should be marked as successfully
                        completed.
        """
        self.success = success
        cancel = []
        mask = TaskState.NOT_FINISHED_MASK
        for task in Task.Iterator(self.task_tree, mask):
            cancel.append(task)
        for task in cancel:
            task.cancel()
        logger.info(f'Cancel with {len(cancel)} remaining', extra=self.log_info())

    def get_task_spec_from_name(self, name):
        """
        Returns the task spec with the given name.

        :type  name: str
        :param name: The name of the task.
        :rtype:  TaskSpec
        :returns: The task spec with the given name.
        """
        return self.spec.get_task_spec_from_name(name)

    def get_tasks_from_spec_name(self, name):
        """
        Returns all tasks whose spec has the given name.

        :type name: str
        :param name: The name of a task spec.
        :rtype: list[Task]
        :returns: A list of tasks that relate to the spec with the given name.
        """
        return [task for task in self.get_tasks_iterator() if task.task_spec.name == name]

    def get_tasks(self, state=TaskState.ANY_MASK):
        """
        Returns a list of Task objects with the given state.

        :type  state: integer
        :param state: A bitmask of states.
        :rtype:  list[Task]
        :returns: A list of tasks.
        """
        return [t for t in Task.Iterator(self.task_tree, state)]

    def get_tasks_iterator(self, state=TaskState.ANY_MASK):
        """
        Returns a iterator of Task objects with the given state.

        :type  state: integer
        :param state: A bitmask of states.
        :rtype:  Task.Iterator
        :returns: A list of tasks.
        """
        return Task.Iterator(self.task_tree, state)

    def get_task_from_id(self, task_id, tasklist=None):
        """
        Returns the task with the given id.

        :type id:integer
        :param id: The id of a task.
        :param tasklist: Optional cache of get_tasks for operations
                         where we are calling multiple times as when we
                         are deserializing the workflow
        :rtype: Task
        :returns: The task with the given id.
        """
        if task_id is None:
            raise WorkflowException('task_id is None', task_spec=self.spec)
        tasklist = tasklist or self.task_tree
        for task in self.task_tree:
            if task.id == task_id:
                return task
        msg = 'A task with the given task_id (%s) was not found' % task_id
        raise TaskNotFoundException(msg, task_spec=self.spec)

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
        """
        task = self.get_task_from_id(task_id)
        return task.reset_token(data)

    def run_next(self, pick_up=True, halt_on_manual=True):
        """
        Runs the next task.
        Returns True if completed, False otherwise.

        :type  pick_up: bool
        :param pick_up: When True, this method attempts to choose the next
                        task not by searching beginning at the root, but by
                        searching from the position at which the last call
                        of complete_next() left off.
        :type  halt_on_manual: bool
        :param halt_on_manual: When True, this method will not attempt to
                        complete any tasks that have manual=True.
                        See :meth:`SpiffWorkflow.specs.TaskSpec.__init__`
        :rtype:  bool
        :returns: True if all tasks were completed, False otherwise.
        """
        # Try to pick up where we left off.
        blacklist = []
        if pick_up and self.last_task is not None:
            try:
                iter = Task.Iterator(self.last_task, TaskState.READY)
                task = next(iter)
            except StopIteration:
                task = None
            self.last_task = None
            if task is not None:
                if not (halt_on_manual and task.task_spec.manual):
                    if task.run():
                        self.last_task = task
                        return True
                blacklist.append(task)

        # Walk through all ready tasks.
        for task in Task.Iterator(self.task_tree, TaskState.READY):
            for blacklisted_task in blacklist:
                if task._is_descendant_of(blacklisted_task):
                    continue
            if not (halt_on_manual and task.task_spec.manual):
                if task.run():
                    self.last_task = task
                    return True
            blacklist.append(task)

        # Walk through all waiting tasks.
        for task in Task.Iterator(self.task_tree, TaskState.WAITING):
            task.task_spec._update(task)
            if not task._has_state(TaskState.WAITING):
                self.last_task = task
                return True
        return False

    def run_all(self, pick_up=True, halt_on_manual=True):
        """
        Runs all branches until completion. This is a convenience wrapper
        around :meth:`complete_next`, and the pick_up argument is passed
        along.

        :type  pick_up: bool
        :param pick_up: Passed on to each call of complete_next().
        :type  halt_on_manual: bool
        :param halt_on_manual: When True, this method will not attempt to
                        complete any tasks that have manual=True.
                        See :meth:`SpiffWorkflow.specs.TaskSpec.__init__`
        """
        while self.run_next(pick_up, halt_on_manual):
            pass

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
