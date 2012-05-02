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

from SpiffWorkflow.util.event import Event
from SpiffWorkflow.Task import Task
from SpiffWorkflow.exceptions import WorkflowException


LOG = logging.getLogger(__name__)


class TaskSpec(object):
    """
    This class implements an abstract base type for all tasks.

    Tasks provide the following signals:
      - B{entered}: called when the state changes to READY or WAITING, at a
        time where properties are not yet initialized.
      - B{reached}: called when the state changes to READY or WAITING, at a
        time where properties are already initialized using property_assign
        and pre-assign.
      - B{ready}: called when the state changes to READY, at a time where
        properties are already initialized using property_assign and
        pre-assign.
      - B{completed}: called when the state changes to COMPLETED, at a time
        before the post-assign variables are assigned.
      - B{cancelled}: called when the state changes to CANCELLED, at a time
        before the post-assign variables are assigned.
      - B{finished}: called when the state changes to COMPLETED or CANCELLED,
        at the last possible time after the post-assign variables are
        assigned and mutexes are released.

    Event sequence is: entered -> reached -> ready -> completed -> finished
        (cancelled may happen at any time)

    The only events where implementing something other than state tracking
    may be useful are the following:
      - Reached: You could mess with the pre-assign variables here, for
        example. Other then that, there is probably no need in a real
        application.
      - Ready: This is where a task could implement custom code, for example
        for triggering an external system. This is also the only event where a
        return value has a meaning (returning non-True will mean that the
        post-assign procedure is skipped.)
    """

    def __init__(self, parent, name, **kwargs):
        """
        Constructor. May also have properties/attributes passed.

        The difference between the assignment of a property using
        properties versus pre_assign and post_assign is that
        changes made using properties are task-local, i.e. they are
        not visible to other tasks.
        Similarly, "defines" are properties that, once defined, can no
        longer be modified.

        @type  parent: L{SpiffWorkflow.specs.WorkflowSpec}
        @param parent: A reference to the parent (usually a workflow).
        @type  name: string
        @param name: A name for the task.
        @type    lock: list(str)
        @keyword lock: A list of mutex names. The mutex is acquired
                       on entry of execute() and released on leave of
                       execute().
        @type    properties: dict((str, object))
        @keyword properties: name/value pairs
        @type    defines: dict((str, object))
        @keyword defines: name/value pairs
        @type    pre_assign: list((str, object))
        @keyword pre_assign: a list of name/value pairs
        @type    post_assign: list((str, object))
        @keyword post_assign: a list of name/value pairs
        """
        assert parent is not None
        assert name   is not None
        if __debug__:
            from SpiffWorkflow.specs import WorkflowSpec  # Can't import above
            assert isinstance(parent, WorkflowSpec)
        self._parent     = parent
        self.id          = None
        self.name        = str(name)
        self.description = kwargs.pop('description', '')
        self.inputs      = []
        self.outputs     = []
        self.manual      = False
        self.internal    = False  # Only for easing debugging.
        self.properties  = kwargs.pop('properties',  {})
        self.defines     = kwargs.pop('defines',     {})
        self.pre_assign  = kwargs.pop('pre_assign',  [])
        self.post_assign = kwargs.pop('post_assign', [])
        self.locks       = kwargs.pop('lock',        [])
        self.lookahead   = 2  # Maximum number of MAYBE predictions.

        # Events.
        self.entered_event   = Event()
        self.reached_event   = Event()
        self.ready_event     = Event()
        self.completed_event = Event()
        self.cancelled_event = Event()
        self.finished_event  = Event()

        self._parent._add_notify(self)
        self.properties.update(self.defines)
        assert self.id is not None

    def _connect_notify(self, taskspec):
        """
        Called by the previous task to let us know that it exists.

        @type  taskspec: TaskSpec
        @param taskspec: The task by which this method is executed.
        """
        self.inputs.append(taskspec)

    def _get_activated_tasks(self, my_task, destination):
        """
        Returns the list of tasks that were activated in the previous
        call of execute(). Only returns tasks that point towards the
        destination task, i.e. those which have destination as a
        descendant.

        @type  my_task: Task
        @param my_task: The associated task in the task tree.
        @type  destination: Task
        @param destination: The destination task.
        """
        return my_task.children

    def _get_activated_threads(self, my_task):
        """
        Returns the list of threads that were activated in the previous
        call of execute().

        @type  my_task: Task
        @param my_task: The associated task in the task tree.
        """
        return my_task.children

    def set_property(self, **kwargs):
        """
        Defines the given property name/value pairs.
        """
        for key in kwargs:
            if key in self.defines:
                msg = "Property %s can not be modified" % key
                raise WorkflowException(msg)
        self.properties.update(kwargs)

    def get_property(self, name, default=None):
        """
        Returns the value of the property with the given name, or the given
        default value if the property does not exist.

        @type  name: string
        @param name: A property name.
        @type  default: string
        @param default: This value is returned if the property does not exist.
        """
        return self.properties.get(name, default)

    def connect(self, taskspec):
        """
        Connect the *following* task to this one. In other words, the
        given task is added as an output task.

        @type  taskspec: TaskSpec
        @param taskspec: The new output task.
        """
        self.outputs.append(taskspec)
        taskspec._connect_notify(self)

    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        if self.id is None:
            raise WorkflowException(self, 'TaskSpec is not yet instanciated.')
        if len(self.inputs) < 1:
            raise WorkflowException(self, 'No input task connected.')

    def _predict(self, my_task, seen=None, looked_ahead=0):
        """
        Updates the branch such that all possible future routes are added
        with the LIKELY flag.

        Should NOT be overwritten! Instead, overwrite the hook (_predict_hook).

        @type  my_task: Task
        @param my_task: The associated task in the task tree.
        @type  seen: list[taskspec]
        @param seen: A list of already visited tasks.
        @type  looked_ahead: integer
        @param looked_ahead: The depth of the predicted path so far.
        """
        if seen is None:
            seen = []
        elif self in seen:
            return
        if not my_task._is_definite():
            seen.append(self)
        if my_task._has_state(Task.MAYBE):
            looked_ahead += 1
            if looked_ahead >= self.lookahead:
                return
        if not my_task._is_finished():
            self._predict_hook(my_task)
        for child in my_task.children:
            child.task_spec._predict(child, seen[:], looked_ahead)

    def _predict_hook(self, my_task):
        if my_task._is_definite():
            child_state = Task.FUTURE
        else:
            child_state = Task.LIKELY
        my_task._update_children(self.outputs, child_state)

    def _update_state(self, my_task):
        """
        Called whenever any event happens that may affect the
        state of this task in the workflow. For example, if a predecessor
        completes it makes sure to call this method so we can react.
        """
        my_task._inherit_attributes()
        if not self._update_state_hook(my_task):
            LOG.debug("_update_state_hook for %s was not positive, so not "
                    "going to READY state" % my_task.get_name())
            return
        self.entered_event.emit(my_task.workflow, my_task)
        my_task._ready()

    def _update_state_hook(self, my_task):
        """
        Typically this method should perform the following actions::

            - Update the state of the corresponding task.
            - Update the predictions for its successors.

        Returning non-False will cause the task to go into READY.
        Returning any other value will cause no action.
        """
        if not my_task.parent._is_finished():
            assert my_task.state != Task.WAITING
            my_task.state = Task.FUTURE
        if my_task._is_predicted():
            self._predict(my_task)
        LOG.debug("'%s'._update_state_hook says parent (%s, state=%s) "
                "is_finished=%s" % (self.name, my_task.parent.get_name(),
                my_task.parent.get_state_name(),
                my_task.parent._is_finished()))
        if my_task.parent._is_finished():
            return True
        return False

    def _on_ready(self, my_task):
        """
        Return True on success, False otherwise.

        @type  my_task: Task
        @param my_task: The associated task in the task tree.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert my_task is not None
        self.test()

        # Acquire locks, if any.
        for lock in self.locks:
            mutex = my_task.workflow._get_mutex(lock)
            if not mutex.testandset():
                return False

        # Assign variables, if so requested.
        for assignment in self.pre_assign:
            assignment.assign(my_task, my_task)

        # Run task-specific code.
        result = self._on_ready_before_hook(my_task)
        self.reached_event.emit(my_task.workflow, my_task)
        if result:
            result = self._on_ready_hook(my_task)

        # Run user code, if any.
        if result:
            result = self.ready_event.emit(my_task.workflow, my_task)

        if result:
            # Assign variables, if so requested.
            for assignment in self.post_assign:
                assignment.assign(my_task, my_task)

        # Release locks, if any.
        for lock in self.locks:
            mutex = my_task.workflow._get_mutex(lock)
            mutex.unlock()

        self.finished_event.emit(my_task.workflow, my_task)
        return result

    def _on_ready_before_hook(self, my_task):
        """
        A hook into _on_ready() that does the task specific work.

        @type  my_task: Task
        @param my_task: The associated task in the task tree.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        return True

    def _on_ready_hook(self, my_task):
        """
        A hook into _on_ready() that does the task specific work.

        @type  my_task: Task
        @param my_task: The associated task in the task tree.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        return True

    def _on_cancel(self, my_task):
        """
        May be called by another task to cancel the operation before it was
        completed.

        Return True on success, False otherwise.

        @type  my_task: Task
        @param my_task: The associated task in the task tree.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        self.cancelled_event.emit(my_task.workflow, my_task)
        return True

    def _on_trigger(self, my_task):
        """
        May be called by another task to trigger a task-specific
        event.

        @type  my_task: Task
        @param my_task: The associated task in the task tree.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        raise NotImplementedError("Trigger not supported by this task.")

    def _on_complete(self, my_task):
        """
        Return True on success, False otherwise. Should not be overwritten,
        overwrite _on_complete_hook() instead.

        @type  my_task: Task
        @param my_task: The associated task in the task tree.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert my_task is not None

        if my_task.workflow.debug:
            print "Executing task:", my_task.get_name()

        if not self._on_complete_hook(my_task):
            return False

        # Notify the Workflow.
        my_task.workflow._task_completed_notify(my_task)

        if my_task.workflow.debug:
            if hasattr(my_task.workflow, "outer_workflow"):
                my_task.workflow.outer_workflow.task_tree.dump()

        self.completed_event.emit(my_task.workflow, my_task)
        return True

    def _on_complete_hook(self, my_task):
        """
        A hook into _on_complete() that does the task specific work.

        @type  my_task: Task
        @param my_task: The associated task in the task tree.
        @rtype:  bool
        @return: True on success, False otherwise.
        """
        # If we have more than one output, implicitly split.
        my_task._update_children(self.outputs)
        return True

    def serialize(self, serializer, **kwargs):
        """
        Serializes the instance using the provided serializer.

        @note: The events of a TaskSpec are not serialized. If you
        use them, make sure to re-connect them once the spec is
        deserialized.

        @type  serializer: L{SpiffWorkflow.storage.Serializer}
        @param serializer: The serializer to use.
        @type  kwargs: dict
        @param kwargs: Passed to the serializer.
        @rtype:  object
        @return: The serialized object.
        """
        return serializer._serialize_task_spec(self, **kwargs)

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state, **kwargs):
        """
        Deserializes the instance using the provided serializer.

        @note: The events of a TaskSpec are not serialized. If you
        use them, make sure to re-connect them once the spec is
        deserialized.

        @type  serializer: L{SpiffWorkflow.storage.Serializer}
        @param serializer: The serializer to use.
        @type  wf_spec: L{SpiffWorkflow.spec.WorkflowSpec}
        @param wf_spec: An instance of the WorkflowSpec.
        @type  s_state: object
        @param s_state: The serialized task specification object.
        @type  kwargs: dict
        @param kwargs: Passed to the serializer.
        @rtype:  TaskSpec
        @return: The task specification instance.
        """
        return serializer._deserialize_task_spec(wf_spec, s_state,
                cls(wf_spec, s_state['name']), **kwargs)
