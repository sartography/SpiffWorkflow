# -*- coding: utf-8 -*-
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

from SpiffWorkflow.bpmn.specs.events.event_definitions import MessageEventDefinition
from .PythonScriptEngine import PythonScriptEngine
from .specs.events.event_types import CatchingEvent
from .specs.events.StartEvent import StartEvent
from .specs.SubWorkflowTask import CallActivity
from ..task import TaskState, Task
from ..workflow import Workflow
from ..exceptions import WorkflowException


class BpmnMessage:

    def __init__(self, correlations, name, payload):

        self.correlations = correlations or {}
        self.name = name
        self.payload = payload


class BpmnWorkflow(Workflow):
    """
    The engine that executes a BPMN workflow. This specialises the standard
    Spiff Workflow class with a few extra methods and attributes.
    """

    def __init__(self, top_level_spec, subprocess_specs=None, name=None, script_engine=None,
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
        self._busy_with_restore = False
        # THIS IS THE LINE THAT LOGS
        super(BpmnWorkflow, self).__init__(top_level_spec, **kwargs)
        self.name = name or top_level_spec.name
        self.subprocess_specs = subprocess_specs or {}
        self.subprocesses = {}
        self.bpmn_messages = []
        self.correlations = {}
        self.__script_engine = script_engine or PythonScriptEngine()
        self.read_only = read_only

    @property
    def script_engine(self):
        # The outermost script engine always takes precedence.
        # All call activities, sub-workflows and DMNs should use the
        # workflow engine of the outermost workflow.
        return self._get_outermost_workflow().__script_engine

    @script_engine.setter
    def script_engine(self, engine):
        self.__script_engine = engine

    def create_subprocess(self, my_task, spec_name, name):

        workflow = self._get_outermost_workflow(my_task)
        subprocess = BpmnWorkflow(
            workflow.subprocess_specs[spec_name], name=name,
            read_only=self.read_only,
            script_engine=self.script_engine,
            parent=my_task.workflow)
        workflow.subprocesses[my_task.id] = subprocess
        return subprocess

    def delete_subprocess(self, my_task):
        workflow = self._get_outermost_workflow(my_task)
        del workflow.subprocesses[my_task.id]

    def get_subprocess(self, my_task):
        workflow = self._get_outermost_workflow(my_task)
        return workflow.subprocesses.get(my_task.id)

    def add_subprocess(self, spec_name, name):

        new = CallActivity(self.spec, name, spec_name)
        self.spec.start.connect(new)
        task = Task(self, new)
        task._ready()
        start = self.get_tasks_from_spec_name('Start', workflow=self)[0]
        start.children.append(task)
        task.parent = start
        return self.subprocesses[task.id]

    def _get_outermost_workflow(self, task=None):
        workflow = task.workflow if task is not None else self
        while workflow != workflow.outer_workflow:
            workflow = workflow.outer_workflow
        return workflow

    def catch(self, event_definition, correlations=None):
        """
        Send an event definition to any tasks that catch it.

        Tasks can always catch events, regardless of their state.  The
        event information is stored in the tasks internal data and processed
        when the task is reached in the workflow.  If a task should only
        receive messages while it is running (eg a boundary event), the task
        should call the event_definition's reset method before executing to
        clear out a stale message.

        :param event_definition: the thrown event
        """
        assert not self.read_only and not self._is_busy_with_restore()

        # Start a subprocess for known specs with start events that catch this
        # This is total hypocritical of me given how I've argued that specs should
        # be immutable, but I see no other way of doing this.
        for name, spec in self.subprocess_specs.items():
            for task_spec in list(spec.task_specs.values()):
                if isinstance(task_spec, StartEvent) and task_spec.event_definition == event_definition:
                    subprocess = self.add_subprocess(spec.name, f'{spec.name}_{len(self.subprocesses)}')
                    subprocess.correlations = correlations or {}
                    start = self.get_tasks_from_spec_name(task_spec.name, workflow=subprocess)[0]
                    task_spec.event_definition.catch(start, event_definition)

        # We need to get all the tasks that catch an event before completing any of them
        # in order to prevent the scenario where multiple boundary events catch the
        # same event and the first executed cancels the rest
        tasks = [ t for t in self.get_catching_tasks() if t.task_spec.catches(t, event_definition, correlations or {}) ]
        for task in tasks:
            task.task_spec.catch(task, event_definition)

        # Figure out if we need to create an extenal message
        if len(tasks) == 0 and isinstance(event_definition, MessageEventDefinition):
            self.bpmn_messages.append(
                BpmnMessage(correlations, event_definition.name, event_definition.payload))

    def get_bpmn_messages(self):
        messages = self.bpmn_messages
        self.bpmn_messages = []
        return messages

    def catch_bpmn_message(self, name, payload, correlations=None):
        event_definition = MessageEventDefinition(name)
        event_definition.payload = payload
        self.catch(event_definition, correlations=correlations)

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
            [t for t in self.get_tasks(TaskState.READY)
             if self._is_engine_task(t.task_spec)])
        while engine_steps:
            for task in engine_steps:
                task.complete()
                if task.task_spec.name == exit_at:
                    return task
            engine_steps = list(
                [t for t in self.get_tasks(TaskState.READY)
                 if self._is_engine_task(t.task_spec)])

    def refresh_waiting_tasks(self):
        """
        Refresh the state of all WAITING tasks. This will, for example, update
        Catching Timer Events whose waiting time has passed.
        """
        assert not self.read_only
        for my_task in self.get_tasks(TaskState.WAITING):
            my_task.task_spec._update(my_task)

    def get_tasks_from_spec_name(self, name, workflow=None):
        return [t for t in self.get_tasks(workflow=workflow) if t.task_spec.name == name]

    def get_tasks(self, state=TaskState.ANY_MASK, workflow=None):
        tasks = []
        top = self._get_outermost_workflow()
        wf = workflow or top
        for task in Workflow.get_tasks(wf):
            subprocess = top.subprocesses.get(task.id)
            if subprocess is not None:
                tasks.extend(subprocess.get_tasks(state, subprocess))
            if task._has_state(state):
                tasks.append(task)
        return tasks

    def _find_task(self, task_id):
        if task_id is None:
            raise WorkflowException(self.spec, 'task_id is None')
        for task in self.get_tasks():
            if task.id == task_id:
                return task
        raise WorkflowException(self.spec,
            f'A task with the given task_id ({task_id}) was not found')

    def complete_task_from_id(self, task_id):
        # I don't even know why we use this stupid function instead of calling task.complete,
        # since all it does is search the task tree and call the method
        task = self._find_task(task_id)
        return task.complete()

    def reset_task_from_id(self, task_id):
        task = self._find_task(task_id)
        if task.workflow.last_task and task.workflow.last_task.data:
            data = task.workflow.last_task.data
        return task.reset_token(data)

    def get_ready_user_tasks(self,lane=None):
        """
        Returns a list of User Tasks that are READY for user action
        """
        if lane is not None:
            return [t for t in self.get_tasks(TaskState.READY)
                       if (not self._is_engine_task(t.task_spec))
                           and (t.task_spec.lane == lane)]
        else:
            return [t for t in self.get_tasks(TaskState.READY)
                       if not self._is_engine_task(t.task_spec)]

    def get_waiting_tasks(self):
        """
        Returns a list of all WAITING tasks
        """
        return self.get_tasks(TaskState.WAITING)

    def get_catching_tasks(self):
        return [ task for task in self.get_tasks() if isinstance(task.task_spec, CatchingEvent) ]

    def _is_busy_with_restore(self):
        if self.outer_workflow == self:
            return self._busy_with_restore
        return self.outer_workflow._is_busy_with_restore()

    def _is_engine_task(self, task_spec):
        return (not hasattr(task_spec, 'is_engine_task') or
                task_spec.is_engine_task())

    def _task_completed_notify(self, task):
        assert (not self.read_only) or self._is_busy_with_restore()
        super(BpmnWorkflow, self)._task_completed_notify(task)

    def _task_cancelled_notify(self, task):
        assert (not self.read_only) or self._is_busy_with_restore()
