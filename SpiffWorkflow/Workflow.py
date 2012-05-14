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
from mutex import mutex
from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow import specs
from SpiffWorkflow.util.event import Event
from Task import Task

LOG = logging.getLogger(__name__)


class TaskIdAssigner(object):
    def __init__(self):
        self.id_pool = 0

    def get_new_id(self):
        self.id_pool += 1
        return self.id_pool


class Workflow(object):
    """
    The engine that executes a workflow.
    It is a essentially a facility for managing all branches.
    A Workflow is also the place that holds the attributes of a running workflow.
    """

    def __init__(self, workflow_spec, deserializing=False, **kwargs):
        """
        Constructor.

        :param deserializing: set to true when deserializing to avoid
        generating tasks twice (and associated problems with multiple
        hierarchies of tasks)
        """
        assert workflow_spec is not None
        LOG.debug("__init__ Workflow instance: %s" % self.__str__())
        self.spec = workflow_spec
        self.task_id_assigner = TaskIdAssigner()
        self.attributes = {}
        self.outer_workflow = kwargs.get('parent', self)
        self.locks = {}
        self.last_task = None
        if deserializing:
            assert 'Root' in workflow_spec.task_specs
            root = workflow_spec.task_specs['Root']  # Probably deserialized
        else:
            root = specs.Simple(workflow_spec, 'Root')
        self.task_tree = Task(self, root)
        self.success = True
        self.debug = False

        # Events.
        self.completed_event = Event()

        if not deserializing:
            # Prevent the root task from being executed.
            self.task_tree.state = Task.COMPLETED
            start = self.task_tree._add_child(self.spec.start)

            self.spec.start._predict(start)
            if 'parent' not in kwargs:
                start.task_spec._update_state(start)

    def is_completed(self):
        """
        Returns True if the entire Workflow is completed, False otherwise.
        """
        mask = Task.NOT_FINISHED_MASK
        iter = Task.Iterator(self.task_tree, mask)
        try:
            iter.next()
        except:
            # No waiting tasks found.
            return True
        return False

    def _get_waiting_tasks(self):
        waiting = Task.Iterator(self.task_tree, Task.WAITING)
        return [w for w in waiting]

    def _task_completed_notify(self, task):
        if task.get_name() == 'End':
            self.attributes.update(task.get_attributes())
        # Update the state of every WAITING task.
        for thetask in self._get_waiting_tasks():
            thetask.task_spec._update_state(thetask)
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

    def get_attribute(self, name, default=None):
        """
        Returns the value of the attribute with the given name, or the given
        default value if the attribute does not exist.

        @type  name: string
        @param name: An attribute name.
        @type  default: obj
        @param default: Return this value if the attribute does not exist.
        @rtype:  obj
        @return: The value of the attribute.
        """
        return self.attributes.get(name, default)

    def cancel(self, success=False):
        """
        Cancels all open tasks in the workflow.

        @type  success: boolean
        @param success: Whether the Workflow should be marked as successfully
                        completed.
        """
        self.success = success
        cancel = []
        mask = Task.NOT_FINISHED_MASK
        for task in Task.Iterator(self.task_tree, mask):
            cancel.append(task)
        for task in cancel:
            task.cancel()

    def get_task_spec_from_name(self, name):
        """
        Returns the task spec with the given name.

        @type  name: string
        @param name: The name of the task.
        @rtype:  TaskSpec
        @return: The task spec with the given name.
        """
        return self.spec.get_task_spec_from_name(name)

    def get_task(self, id):
        """
        Returns the task with the given id.

        @type id:integer
        @param id: The id of a task.
        @rtype: Task
        @return: The task with the given id.
        """
        tasks = [task for task in self.get_tasks() if task.id == id]
        return tasks[0] if len(tasks) == 1 else None

    def get_tasks(self, state=Task.ANY_MASK):
        """
        Returns a list of Task objects with the given state.

        @type  state: integer
        @param state: A bitmask of states.
        @rtype:  list[Task]
        @return: A list of tasks.
        """
        return [t for t in Task.Iterator(self.task_tree, state)]

    def complete_task_from_id(self, task_id):
        """
        Runs the task with the given id.

        @type  task_id: integer
        @param task_id: The id of the Task object.
        """
        if task_id is None:
            raise WorkflowException(self.spec, 'task_id is None')
        for task in self.task_tree:
            if task.id == task_id:
                return task.complete()
        msg = 'A task with the given task_id (%s) was not found' % task_id
        raise WorkflowException(self.spec, msg)

    def complete_next(self, pick_up=True):
        """
        Runs the next task.
        Returns True if completed, False otherwise.

        @type  pick_up: boolean
        @param pick_up: When True, this method attempts to choose the next
                        task not by searching beginning at the root, but by
                        searching from the position at which the last call
                        of complete_next() left off.
        @rtype:  boolean
        @return: True if all tasks were completed, False otherwise.
        """
        # Try to pick up where we left off.
        blacklist = []
        if pick_up and self.last_task is not None:
            try:
                iter = Task.Iterator(self.last_task, Task.READY)
                next = iter.next()
            except:
                next = None
            self.last_task = None
            if next is not None:
                if next.complete():
                    self.last_task = next
                    return True
                blacklist.append(next)

        # Walk through all ready tasks.
        for task in Task.Iterator(self.task_tree, Task.READY):
            for blacklisted_task in blacklist:
                if task._is_descendant_of(blacklisted_task):
                    continue
            if task.complete():
                self.last_task = task
                return True
            blacklist.append(task)

        # Walk through all waiting tasks.
        for task in Task.Iterator(self.task_tree, Task.WAITING):
            task.task_spec._update_state(task)
            if not task._has_state(Task.WAITING):
                self.last_task = task
                return True
        return False

    def complete_all(self, pick_up=True):
        """
        Runs all branches until completion. This is a convenience wrapper
        around complete_next(), and the pick_up argument is passed along.

        @type  pick_up: boolean
        @param pick_up: Passed on to each call of complete_next().
        """
        while self.complete_next(pick_up):
            pass

    def get_dump(self):
        """
        Returns a complete dump of the current internal task tree for
        debugging.

        @rtype:  string
        @return: The debug information.
        """
        return self.task_tree.get_dump()

    def dump(self):
        """
        Like get_dump(), but prints the output to the terminal instead of
        returning it.
        """
        print self.task_tree.dump()

    def serialize(self, serializer, **kwargs):
        """
        Serializes a Workflow instance using the provided serializer.

        @type  serializer: L{SpiffWorkflow.storage.Serializer}
        @param serializer: The serializer to use.
        @type  kwargs: dict
        @param kwargs: Passed to the serializer.
        @rtype:  object
        @return: The serialized workflow.
        """
        return serializer.serialize_workflow(self, **kwargs)

    @classmethod
    def deserialize(cls, serializer, s_state, **kwargs):
        """
        Deserializes a Workflow instance using the provided serializer.

        @type  serializer: L{SpiffWorkflow.storage.Serializer}
        @param serializer: The serializer to use.
        @type  s_state: object
        @param s_state: The serialized workflow.
        @type  kwargs: dict
        @param kwargs: Passed to the serializer.
        @rtype:  Workflow
        @return: The workflow instance.
        """
        return serializer.deserialize_workflow(s_state, **kwargs)
