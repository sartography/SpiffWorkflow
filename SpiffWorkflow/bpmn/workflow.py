# -*- coding: utf-8 -*-
from __future__ import division
# Copyright (C) 2012 Matthew Hampton
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
from .PythonScriptEngine import PythonScriptEngine
from ..task import Task
from ..workflow import Workflow


class BpmnWorkflow(Workflow):
    """
    The engine that executes a BPMN workflow. This specialises the standard
    Spiff Workflow class with a few extra methods and attributes.
    """

    def __init__(self, workflow_spec, name=None, script_engine=None,
                 read_only=False, **kwargs):
        """
        Constructor.

        :param script_engine: set to an extension of PythonScriptEngine if you
        need a specialised version. Defaults to the script engine of the top
        most workflow, or to the PythonScriptEngine if none is provided.

        :param read_only: If this parameter is set then the workflow state
        cannot change. It can only be queried to find out about the current
        state. This is used in conjunction with the CompactWorkflowSerializer
        to provide read only access to a previously saved workflow.
        """
        super(BpmnWorkflow, self).__init__(workflow_spec, **kwargs)
        self.name = name or workflow_spec.name
        self.__script_engine = script_engine or PythonScriptEngine()
        self._busy_with_restore = False
        self.read_only = read_only

    @property
    def script_engine(self):
        # The outermost script engine always takes precedence.
        # All call activities, sub-workflows and DMNs should use the
        # workflow engine of the outermost workflow.
        outer_workflow = self.outer_workflow
        script_engine = self.__script_engine

        while outer_workflow:
            script_engine = outer_workflow.__script_engine
            if outer_workflow == outer_workflow.outer_workflow:
                break
            else:
                outer_workflow = outer_workflow.outer_workflow
        return script_engine

    @script_engine.setter
    def script_engine(self, engine):
        self.__script_engine = engine


    def accept_message(self, message):
        """
        Indicate to the workflow that a message has been received. The message
        will be processed by any waiting Intermediate or Boundary Message
        Events, that are waiting for the message.
        """
        assert not self.read_only
        self.refresh_waiting_tasks()
        self.do_engine_steps()
        for my_task in Task.Iterator(self.task_tree, Task.WAITING):
            my_task.task_spec.accept_message(my_task, message)

    def do_engine_steps(self, exit_at = None):
        """
        Execute any READY tasks that are engine specific (for example, gateways
        or script tasks). This is done in a loop, so it will keep completing
        those tasks until there are only READY User tasks, or WAITING tasks
        left.

        :param exit_at: After executing a task with a name matching this param return the task object
        """
        assert not self.read_only
        engine_steps = list(
            [t for t in self.get_tasks(Task.READY)
             if self._is_engine_task(t.task_spec)])
        while engine_steps:
            for task in engine_steps:
                task.complete()
                if task.task_spec.name == exit_at:
                    return task
            engine_steps = list(
                [t for t in self.get_tasks(Task.READY)
                 if self._is_engine_task(t.task_spec)])
    def refresh_waiting_tasks(self):
        """
        Refresh the state of all WAITING tasks. This will, for example, update
        Catching Timer Events whose waiting time has passed.
        """
        assert not self.read_only
        for my_task in self.get_tasks(Task.WAITING):
            my_task.task_spec._update(my_task)

    def get_ready_user_tasks(self,lane=None):
        """
        Returns a list of User Tasks that are READY for user action
        """
        if lane is not None:
            return [t for t in self.get_tasks(Task.READY)
                       if (not self._is_engine_task(t.task_spec))
                           and (t.task_spec.lane == lane)]
        else:
            return [t for t in self.get_tasks(Task.READY)
                       if not self._is_engine_task(t.task_spec)]

    def get_waiting_tasks(self):
        """
        Returns a list of all WAITING tasks
        """
        return self.get_tasks(Task.WAITING)

    def _is_busy_with_restore(self):
        if self.outer_workflow == self:
            return self._busy_with_restore
        return self.outer_workflow._is_busy_with_restore()

    def _is_engine_task(self, task_spec):
        return (not hasattr(task_spec, 'is_engine_task') or
                task_spec.is_engine_task())

    def _task_completed_notify(self, task):
        assert (not self.read_only) or self._is_busy_with_restore()
        self.last_task = task
        super(BpmnWorkflow, self)._task_completed_notify(task)

    def _task_cancelled_notify(self, task):
        assert (not self.read_only) or self._is_busy_with_restore()
