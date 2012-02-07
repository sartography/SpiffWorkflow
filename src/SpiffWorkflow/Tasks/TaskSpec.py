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
from SpiffWorkflow.util.event import Event
from SpiffWorkflow.Task import Task
from SpiffWorkflow.Exception import WorkflowException
from SpiffWorkflow.Operators import valueof

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
        at the last possible time and after the post-assign variables are 
        assigned.
    """

    def __init__(self, parent, name, **kwargs):
        """
        Constructor. May also have properties/attributes passed.

        The difference between the assignment of a property using 
        property_assign versus pre_assign and post_assign is that 
        changes made using property_assign are task-local, i.e. they are 
        not visible to other tasks.
        Similarly, "defines" are properties that, once defined, can no 
        longer be modified.

        @type  parent: Workflow
        @param parent: A reference to the parent (usually a workflow).
        @type  name: string
        @param name: A name for the task.
        @type  kwargs: dict
        @param kwargs: The following options are supported:
            - lock: a list of locks that is aquired on entry of
              execute() and released on leave of execute().
            - property_assign: a list of attribute name/value pairs
            - pre_assign: a list of attribute name/value pairs
            - post_assign: a list of attribute name/value pairs
        """
        assert parent is not None
        assert name   is not None
        self._parent     = parent
        self.id          = None
        self.name        = str(name)
        self.description = kwargs.get('description', '')
        self.inputs      = []
        self.outputs     = []
        self.manual      = False
        self.internal    = False  # Only for easing debugging.
        self.cancelled   = False
        self.properties  = kwargs.get('properties',  {})
        self.defines     = kwargs.get('defines',     {})
        self.pre_assign  = kwargs.get('pre_assign',  [])
        self.post_assign = kwargs.get('post_assign', [])
        self.locks       = kwargs.get('lock',        [])
        self.lookahead   = 2  # Maximum number of MAYBE predictions.

        # Events.
        self.entered_event   = Event()
        self.reached_event   = Event()
        self.ready_event     = Event()
        self.completed_event = Event()

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
        destination node, i.e. those which have destination as a 
        descendant.

        @type  my_task: Task
        @param my_task: The associated node in the task tree.
        @type  destination: Task
        @param destination: The destination node.
        """
        return my_task.children


    def _get_activated_threads(self, my_task):
        """
        Returns the list of threads that were activated in the previous 
        call of execute().

        @type  my_task: Task
        @param my_task: The associated node in the task tree.
        """
        return my_task.children


    def set_property(self, **kwargs):
        """
        Defines the given property name/value pairs.
        """
        for key in kwargs:
            if self.defines.has_key(key):
                msg = "Property %s can not be modified" % key
                raise Exception.WorkflowException(msg)
        self.properties.update(kwargs)


    def get_property(self, name, default = None):
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
        @param taskspec: The new output node.
        """
        self.outputs.append(taskspec)
        taskspec._connect_notify(self)


    def test(self):
        """
        Checks whether all required attributes are set. Throws an exception
        if an error was detected.
        """
        if self.id is None:
            raise Exception.WorkflowException(self, 'TaskSpec is not yet instanciated.')
        if len(self.inputs) < 1:
            raise Exception.WorkflowException(self, 'No input task connected.')


    def _predict(self, my_task, seen = None, looked_ahead = 0):
        """
        Updates the branch such that all possible future routes are added
        with the LIKELY flag.

        Should NOT be overwritten! Instead, overwrite the hook (_predict_hook).

        @type  my_task: Task
        @param my_task: The associated node in the task tree.
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
        for node in my_task.children:
            node.spec._predict(node, seen[:], looked_ahead)


    def _predict_hook(self, my_task):
        if my_task._is_definite():
            child_state = Task.FUTURE
        else:
            child_state = Task.LIKELY
        my_task._update_children(self.outputs, child_state)


    def _update_state(self, my_task):
        my_task._inherit_attributes()
        if not self._update_state_hook(my_task):
            return
        self.entered_event.emit(my_task.job, my_task)
        my_task._ready()


    def _update_state_hook(self, my_task):
        was_predicted = my_task._is_predicted()
        if not my_task.parent._is_finished():
            my_task.state = Task.FUTURE
        if was_predicted:
            self._predict(my_task)
        if my_task.parent._is_finished():
            return True
        return False


    def _on_ready(self, my_task):
        """
        Return True on success, False otherwise.

        @type  my_task: Task
        @param my_task: The associated node in the task tree.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert my_task is not None
        assert not self.cancelled
        self.test()

        # Acquire locks, if any.
        for lock in self.locks:
            mutex = my_task.job._get_mutex(lock)
            if not mutex.testandset():
                return False

        # Assign variables, if so requested.
        for assignment in self.pre_assign:
            assignment.assign(my_task, my_task)

        # Run task-specific code.
        result = self._on_ready_before_hook(my_task)
        self.reached_event.emit(my_task.job, my_task)
        if result:
            result = self._on_ready_hook(my_task)

        # Run user code, if any.
        if result:
            result = self.ready_event.emit(my_task.job, my_task)

        if result:
            # Assign variables, if so requested.
            for assignment in self.post_assign:
                assignment.assign(my_task, my_task)

        # Release locks, if any.
        for lock in self.locks:
            mutex = my_task.job._get_mutex(lock)
            mutex.unlock()
        return result


    def _on_ready_before_hook(self, my_task):
        """
        A hook into _on_ready() that does the task specific work.

        @type  my_task: Task
        @param my_task: The associated node in the task tree.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        return True


    def _on_ready_hook(self, my_task):
        """
        A hook into _on_ready() that does the task specific work.

        @type  my_task: Task
        @param my_task: The associated node in the task tree.
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
        @param my_task: The associated node in the task tree.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        return True


    def _on_trigger(self, my_task):
        """
        May be called by another task to trigger a task-specific
        event.

        @type  my_task: Task
        @param my_task: The associated node in the task tree.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        raise NotImplementedError("Trigger not supported by this task.")


    def _on_complete(self, my_task):
        """
        Return True on success, False otherwise. Should not be overwritten,
        overwrite _on_complete_hook() instead.

        @type  my_task: Task
        @param my_task: The associated node in the task tree.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        assert my_task is not None
        assert not self.cancelled

        if my_task.job.debug:
            print "Executing node:", my_task.get_name()

        if not self._on_complete_hook(my_task):
            return False

        # Notify the Job.
        my_task.job._task_completed_notify(my_task)

        if my_task.job.debug:
            my_task.job.outer_job.task_tree.dump()

        self.completed_event.emit(my_task.job, my_task)
        return True


    def _on_complete_hook(self, my_task):
        """
        A hook into _on_complete() that does the task specific work.

        @type  my_task: Task
        @param my_task: The associated node in the task tree.
        @rtype:  boolean
        @return: True on success, False otherwise.
        """
        # If we have more than one output, implicitly split.
        my_task._update_children(self.outputs)
        return True
