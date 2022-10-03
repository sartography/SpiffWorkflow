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
from abc import abstractmethod

from ..util.event import Event
from ..task import TaskState
from ..exceptions import WorkflowException


class TaskSpec(object):

    """
    This class implements an abstract base type for all tasks.

    Tasks provide the following signals:
      - **entered**: called when the state changes to READY or WAITING, at a
        time where spec data is not yet initialized.
      - **reached**: called when the state changes to READY or WAITING, at a
        time where spec data is already initialized using data_assign
        and pre-assign.
      - **ready**: called when the state changes to READY, at a time where
        spec data is already initialized using data_assign and
        pre-assign.
      - **completed**: called when the state changes to COMPLETED, at a time
        before the post-assign variables are assigned.
      - **cancelled**: called when the state changes to CANCELLED, at a time
        before the post-assign variables are assigned.
      - **finished**: called when the state changes to COMPLETED or CANCELLED,
        at the last possible time after the post-assign variables are
        assigned and mutexes are released.

    Event sequence is: entered -> reached -> ready -> completed -> finished
        (cancelled may happen at any time)

    The only events where implementing something other than state tracking
    may be useful are the following:_
      - Reached: You could mess with the pre-assign variables here, for
        example. Other then that, there is probably no need in a real
        application.
      - Ready: This is where a task could implement custom code, for example
        for triggering an external system. This is also the only event where a
        return value has a meaning (returning non-True will mean that the
        post-assign procedure is skipped.)
    """

    def __init__(self, wf_spec, name, **kwargs):
        """
        Constructor.

        The difference between the assignment of a data value using
        the data argument versus pre_assign and post_assign is that
        changes made using data are task-local, i.e. they are
        not visible to other tasks.
        Similarly, "defines" are spec data fields that, once defined, can
        no longer be modified.

        :type  wf_spec: WorkflowSpec
        :param wf_spec: A reference to the workflow specification that owns it.
        :type  name: string
        :param name: A name for the task.
        :type  lock: list(str)
        :param lock: A list of mutex names. The mutex is acquired
                     on entry of execute() and released on leave of
                     execute().
        :type  manual: bool
        :param manual: Whether this task requires a manual action to complete.
        :type  data: dict((str, object))
        :param data: name/value pairs
        :type  defines: dict((str, object))
        :param defines: name/value pairs
        :type  pre_assign: list((str, object))
        :param pre_assign: a list of name/value pairs
        :type  post_assign: list((str, object))
        :param post_assign: a list of name/value pairs
        :type  position: dict((str, object))
        :param position: a dict containing an 'x' and 'y' with coordinates
                            that describe where the element occurred in the
                            diagram.
        """
        assert wf_spec is not None
        assert name is not None
        self._wf_spec = wf_spec
        self.id = None
        self.name = str(name)
        self.description = kwargs.get('description', '')
        self.inputs = []
        self.outputs = []
        self.manual = kwargs.get('manual', False)
        self.internal = False  # Only for easing debugging.
        self.data = kwargs.get('data', {})
        self.defines = kwargs.get('defines', {})
        self.pre_assign = kwargs.get('pre_assign',[])
        self.post_assign = kwargs.get('post_assign', [])
        self.locks = kwargs.get('lock', [])
        self.lookahead = 2  # Maximum number of MAYBE predictions.

        # Events.
        self.entered_event = Event()
        self.reached_event = Event()
        self.ready_event = Event()
        self.completed_event = Event()
        self.cancelled_event = Event()
        self.finished_event = Event()

        self._wf_spec._add_notify(self)
        self.data.update(self.defines)
        assert self.id is not None

    @property
    def spec_type(self):
        return f'{self.__class__.__module__}.{self.__class__.__name__}'

    def _connect_notify(self, taskspec):
        """
        Called by the previous task to let us know that it exists.

        :type  taskspec: TaskSpec
        :param taskspec: The task by which this method is executed.
        """
        self.inputs.append(taskspec)

    def ancestors(self):
        """Returns list of ancestor task specs based on inputs"""
        results = []

        def recursive_find_ancestors(task, stack):
            for input in task.inputs:
                if input not in stack:
                    stack.append(input)
                    recursive_find_ancestors(input, stack)
        recursive_find_ancestors(self, results)

        return results

    def _get_activated_tasks(self, my_task, destination):
        """
        Returns the list of tasks that were activated in the previous
        call of execute(). Only returns tasks that point towards the
        destination task, i.e. those which have destination as a
        descendant.

        :type  my_task: Task
        :param my_task: The associated task in the task tree.
        :type  destination: Task
        :param destination: The destination task.
        """
        return my_task.children

    def _get_activated_threads(self, my_task):
        """
        Returns the list of threads that were activated in the previous
        call of execute().

        :type  my_task: Task
        :param my_task: The associated task in the task tree.
        """
        return my_task.children

    def set_data(self, **kwargs):
        """
        Defines the given data field(s) using the given name/value pairs.
        """
        for key in kwargs:
            if key in self.defines:
                msg = "Spec data %s can not be modified" % key
                raise WorkflowException(self, msg)
        self.data.update(kwargs)

    def get_data(self, name, default=None):
        """
        Returns the value of the data field with the given name, or the
        given default value if the data was not defined.

        :type  name: string
        :param name: The name of the data field.
        :type  default: string
        :param default: Returned if the data field is not defined.
        """
        return self.data.get(name, default)

    def connect(self, taskspec):
        """
        Connect the *following* task to this one. In other words, the
        given task is added as an output task.

        :type  taskspec: TaskSpec
        :param taskspec: The new output task.
        """
        self.outputs.append(taskspec)
        taskspec._connect_notify(self)

    def follow(self, taskspec):
        """
        Make this task follow the provided one. In other words, this task is
        added to the given task outputs.

        This is an alias to connect, just easier to understand when reading
        code - ex: my_task.follow(the_other_task)
        Adding it after being confused by .connect one times too many!

        :type  taskspec: TaskSpec
        :param taskspec: The task to follow.
        """
        taskspec.connect(self)

    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        # if self.id is None:
        #    raise WorkflowException(self, 'TaskSpec is not yet instanciated.')
        if len(self.inputs) < 1:
            raise WorkflowException(self, 'No input task connected.')

    def _predict(self, my_task, seen=None, looked_ahead=0):
        """
        Updates the branch such that all possible future routes are added.

        Should NOT be overwritten! Instead, overwrite _predict_hook().

        :type  my_task: Task
        :param my_task: The associated task in the task tree.
        :type  seen: list[taskspec]
        :param seen: A list of already visited tasks.
        :type  looked_ahead: integer
        :param looked_ahead: The depth of the predicted path so far.
        """
        if my_task._is_finished():
            return
        if seen is None:
            seen = []
        elif self in seen:
            return
        if not my_task._is_finished():
            self._predict_hook(my_task)
        if not my_task._is_definite():
            if looked_ahead + 1 >= self.lookahead:
                return
            seen.append(self)
        for child in my_task.children:
            child.task_spec._predict(child, seen[:], looked_ahead + 1)

    def _predict_hook(self, my_task):
        # If the task's status is not predicted, we default to FUTURE
        # for all it's outputs.
        # Otherwise, copy my own state to the children.
        if my_task._is_definite():
            best_state = TaskState.FUTURE
        else:
            best_state = my_task.state

        my_task._sync_children(self.outputs, best_state)
        for child in my_task.children:
            if not child._is_definite():
                child._set_state(best_state)

    def _update(self, my_task):
        """
        Called whenever any event happens that may affect the
        state of this task in the workflow. For example, if a predecessor
        completes it makes sure to call this method so we can react.
        """
        my_task._inherit_data()
        self._update_hook(my_task)

    def _update_hook(self, my_task):
        """
        Typically this method should perform the following actions::

            - Update the state of the corresponding task.
            - Update the predictions for its successors.

        Returning non-False will cause the task to go into READY.
        Returning any other value will cause no action.
        """
        if my_task._is_predicted():
            self._predict(my_task)
        if not my_task.parent._is_finished():
            return
        self.entered_event.emit(my_task.workflow, my_task)
        my_task._ready()

    def _on_ready(self, my_task):
        """
        Return True on success, False otherwise.

        :type  my_task: Task
        :param my_task: The associated task in the task tree.
        """
        assert my_task is not None
        self.test()

        # Acquire locks, if any.
        for lock in self.locks:
            mutex = my_task.workflow._get_mutex(lock)
            if not mutex.testandset():
                return

        # Assign variables, if so requested.
        for assignment in self.pre_assign:
            assignment.assign(my_task, my_task)

        # Run task-specific code.
        self._on_ready_before_hook(my_task)
        self.reached_event.emit(my_task.workflow, my_task)
        self._on_ready_hook(my_task)

        # Run user code, if any.
        if self.ready_event.emit(my_task.workflow, my_task):
            # Assign variables, if so requested.
            for assignment in self.post_assign:
                assignment.assign(my_task, my_task)

        # Release locks, if any.
        for lock in self.locks:
            mutex = my_task.workflow._get_mutex(lock)
            mutex.unlock()

        self.finished_event.emit(my_task.workflow, my_task)

    def _on_ready_before_hook(self, my_task):
        """
        A hook into _on_ready() that does the task specific work.

        :type  my_task: Task
        :param my_task: The associated task in the task tree.
        """
        pass

    def _on_ready_hook(self, my_task):
        """
        A hook into _on_ready() that does the task specific work.

        :type  my_task: Task
        :param my_task: The associated task in the task tree.
        """
        pass

    def _on_cancel(self, my_task):
        """
        May be called by another task to cancel the operation before it was
        completed.

        :type  my_task: Task
        :param my_task: The associated task in the task tree.
        """
        self.cancelled_event.emit(my_task.workflow, my_task)

    def _on_trigger(self, my_task):
        """
        May be called by another task to trigger a task-specific
        event.

        :type  my_task: Task
        :param my_task: The associated task in the task tree.
        :rtype:  boolean
        :returns: True on success, False otherwise.
        """
        raise NotImplementedError("Trigger not supported by this task.")

    def _on_complete(self, my_task):
        """
        Return True on success, False otherwise. Should not be overwritten,
        overwrite _on_complete_hook() instead.

        :type  my_task: Task
        :param my_task: The associated task in the task tree.
        :rtype:  boolean
        :returns: True on success, False otherwise.
        """
        assert my_task is not None

        if my_task.workflow.debug:
            print("Executing %s: %s (%s)" % (
                my_task.task_spec.__class__.__name__,
                my_task.get_name(), my_task.get_description()))

        # We have to set the last task here, because the on_complete_hook
        # of a loopback task may overwrite what the last_task will be.
        my_task.workflow.last_task = my_task
        self._on_complete_hook(my_task)
        my_task.workflow._task_completed_notify(my_task)

        if my_task.workflow.debug:
            if hasattr(my_task.workflow, "outer_workflow"):
                my_task.workflow.outer_workflow.task_tree.dump()

        self.completed_event.emit(my_task.workflow, my_task)
        return True

    def _on_complete_hook(self, my_task):
        """
        A hook into _on_complete() that does the task specific work.

        :type  my_task: Task
        :param my_task: The associated task in the task tree.
        :rtype:  bool
        :returns: True on success, False otherwise.
        """
        # If we have more than one output, implicitly split.
        for child in my_task.children:
            child.task_spec._update(child)

    @abstractmethod
    def serialize(self, serializer, **kwargs):
        """
        Serializes the instance using the provided serializer.

        .. note::

            The events of a TaskSpec are not serialized. If you
            use them, make sure to re-connect them once the spec is
            deserialized.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :type  kwargs: dict
        :param kwargs: Passed to the serializer.
        :rtype:  object
        :returns: The serialized object.
        """
        module = self.__class__.__module__
        class_name = module + '.' + self.__class__.__name__

        return {
                  'id':self.id,
                  'class': class_name,
                  'name':self.name,
                  'description':self.description,
                  'inputs':[x.id for x in self.inputs],
                  'outputs':[x.id for x in self.outputs],
                  'manual':self.manual,
                  'internal':self.internal,
                  'data':self.data,
                  'defines':self.defines,
                  'pre_assign':self.pre_assign,
                  'post_assign':self.post_assign,
                  'locks':self.locks,
                  'lookahead':self.lookahead,
                  }

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state, **kwargs):
        """
        Deserializes the instance using the provided serializer.

        .. note::

            The events of a TaskSpec are not serialized. If you
            use them, make sure to re-connect them once the spec is
            deserialized.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :type  wf_spec: :class:`SpiffWorkflow.spec.WorkflowSpec`
        :param wf_spec: An instance of the WorkflowSpec.
        :type  s_state: object
        :param s_state: The serialized task specification object.
        :type  kwargs: dict
        :param kwargs: Passed to the serializer.
        :rtype:  TaskSpec
        :returns: The task specification instance.
        """
        print(s_state)
        print(wf_spec)
        out = cls(wf_spec,s_state.get('name'))
        out.id = s_state.get('id')
        out.name = s_state.get('name')
        out.description = s_state.get('description')
        out.inputs = s_state.get('inputs')
        out.outputs = s_state.get('outputs')
        out.manual = s_state.get('manual')
        out.internal = s_state.get('internal')
        out.data = s_state.get('data')
        out.defines = s_state.get('defines')
        out.pre_assign = s_state.get('pre_assign')
        out.post_assign = s_state.get('post_assign')
        out.locks = s_state.get('locks')
        out.lookahead = s_state.get('lookahead')
        return out

    def task_should_set_children_future(self, my_task):
        """
        Hook to allow a task_spec to indicate if a task should
        set_future_children.

        Subclasses can override to influence this decision.
        """
        return my_task.state == TaskState.COMPLETED or my_task.state == TaskState.READY

    def task_will_set_children_future(self, my_task):
        """
        Called right before a task runs the logic for set_children_future if
        task_should_set_children_future returns True.

        Subclasses can override to perform work during that stage of execution.
        """
        pass
