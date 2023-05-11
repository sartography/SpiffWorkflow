# Copyright (C) 2012 Matthew Hampton, 2023 Sartography
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

import copy

from SpiffWorkflow.task import TaskState, Task
from SpiffWorkflow.workflow import Workflow
from SpiffWorkflow.exceptions import WorkflowException, TaskNotFoundException
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskException

from SpiffWorkflow.bpmn.specs.mixins.events.event_types import CatchingEvent
from SpiffWorkflow.bpmn.specs.mixins.events.start_event import StartEvent
from SpiffWorkflow.bpmn.specs.mixins.subworkfow_task import CallActivity
from SpiffWorkflow.bpmn.specs.event_definitions import (
    MessageEventDefinition,
    MultipleEventDefinition,
    NamedEventDefinition,
    TimerEventDefinition,
)

from SpiffWorkflow.bpmn.specs.events.IntermediateEvent import _BoundaryEventParent
from .PythonScriptEngine import PythonScriptEngine


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

    def __init__(self, top_level_spec, subprocess_specs=None, name=None, script_engine=None, **kwargs):
        """
        Constructor.

        :param script_engine: set to an extension of PythonScriptEngine if you
        need a specialised version. Defaults to the script engine of the top
        most workflow, or to the PythonScriptEngine if none is provided.
        """
        super(BpmnWorkflow, self).__init__(top_level_spec, **kwargs)
        self.name = name or top_level_spec.name
        self.subprocess_specs = subprocess_specs or {}
        self.subprocesses = {}
        self.bpmn_messages = []
        self.correlations = {}
        self.__script_engine = script_engine or PythonScriptEngine()

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
        # This creates a subprocess for an existing task
        workflow = self._get_outermost_workflow(my_task)
        subprocess = BpmnWorkflow(
            workflow.subprocess_specs[spec_name], name=name,
            script_engine=self.script_engine,
            parent=my_task.workflow)
        workflow.subprocesses[my_task.id] = subprocess
        return subprocess

    def delete_subprocess(self, my_task):
        workflow = self._get_outermost_workflow(my_task)
        if my_task.id in workflow.subprocesses:
            del workflow.subprocesses[my_task.id]

    def get_subprocess(self, my_task):
        workflow = self._get_outermost_workflow(my_task)
        return workflow.subprocesses.get(my_task.id)

    def connect_subprocess(self, spec_name, name):
        # This creates a new task associated with a process when an event that kicks of a process is received
        new = CallActivity(self.spec, name, spec_name)
        self.spec.start.connect(new)
        task = Task(self, new)
        start = self.get_tasks_from_spec_name('Start', workflow=self)[0]
        start.children.append(task)
        task.parent = start
        # This (indirectly) calls create_subprocess
        task.task_spec._update(task)
        return self.subprocesses[task.id]

    def _get_outermost_workflow(self, task=None):
        workflow = task.workflow if task is not None else self
        while workflow != workflow.outer_workflow:
            workflow = workflow.outer_workflow
        return workflow

    def _get_or_create_subprocess(self, task_spec, wf_spec):
        if isinstance(task_spec.event_definition, MultipleEventDefinition):
            for sp in self.subprocesses.values():
                start = sp.get_tasks_from_spec_name(task_spec.name)
                if len(start) and start[0].state == TaskState.WAITING:
                    return sp
        return self.connect_subprocess(wf_spec.name, f'{wf_spec.name}_{len(self.subprocesses)}')

    def catch(self, event_definition, correlations=None):
        """

        Tasks can always catch events, regardless of their state.  The
        event information is stored in the tasks internal data and processed
        when the task is reached in the workflow.  If a task should only
        receive messages while it is running (eg a boundary event), the task
        should call the event_definition's reset method before executing to
        clear out a stale message.

        We might be catching an event that was thrown from some other part of
        our own workflow, and it needs to continue out, but if it originated
        externally, we should not pass it on.

        :param event_definition: the thrown event
        """
        # Start a subprocess for known specs with start events that catch this
        # This is total hypocritical of me given how I've argued that specs should
        # be immutable, but I see no other way of doing this.
        for name, spec in self.subprocess_specs.items():
            for task_spec in list(spec.task_specs.values()):
                if isinstance(task_spec, StartEvent) and task_spec.event_definition == event_definition:
                    subprocess = self._get_or_create_subprocess(task_spec, spec)
                    subprocess.correlations.update(correlations or {})

        # We need to get all the tasks that catch an event before completing any of them
        # in order to prevent the scenario where multiple boundary events catch the
        # same event and the first executed cancels the rest
        tasks = [ t for t in self.get_catching_tasks() if t.task_spec.catches(t, event_definition, correlations or {}) ]
        for task in tasks:
            task.task_spec.catch(task, event_definition)

        # Move any tasks that received message to READY
        self.refresh_waiting_tasks()

        # Figure out if we need to create an external message
        if len(tasks) == 0 and isinstance(event_definition, MessageEventDefinition):
            self.bpmn_messages.append(
                BpmnMessage(correlations, event_definition.name, event_definition.payload))

    def get_bpmn_messages(self):
        messages = self.bpmn_messages
        self.bpmn_messages = []
        return messages

    def catch_bpmn_message(self, name, payload):
        """Allows this workflow to catch an externally generated bpmn message.
        Raises an error if this workflow is not waiting on the given message."""
        event_definition = MessageEventDefinition(name)
        event_definition.payload = payload

        # There should be one and only be one task that can accept the message
        # (messages are one to one, not one to many)
        tasks = [t for t in self.get_waiting_tasks() if t.task_spec.event_definition == event_definition]
        if len(tasks) == 0:
            raise WorkflowException(
                f"This process is not waiting on a message named '{event_definition.name}'")
        if len(tasks) > 1:
            raise WorkflowException(
                f"This process has multiple tasks waiting on the same message '{event_definition.name}', which is not supported. ")

        task = tasks[0]
        conversation = task.task_spec.event_definition.conversation()
        if not conversation:
            raise WorkflowTaskException(
                f"The waiting task and message payload can not be matched to any correlation key (conversation topic).  "
                f"And is therefor unable to respond to the given message.", task)
        updated_props = self._correlate(conversation, payload, task)
        task.task_spec.catch(task, event_definition)
        self.refresh_waiting_tasks()
        self.correlations[conversation] = updated_props

    def _correlate(self, conversation, payload, task):
        """Assures that the provided payload correlates to the given
        task's event definition and this workflows own correlation
        properties.  Returning an updated property list if successful"""
        receive_event = task.task_spec.event_definition
        current_props = self.correlations.get(conversation, {})
        updated_props = copy.copy(current_props)
        for prop in receive_event.correlation_properties:
            try:
                new_val = self.script_engine._evaluate(
                    prop.retrieval_expression, payload
                )
            except Exception as e:
                raise WorkflowTaskException("Unable to accept the BPMN message. "
                                            "The payload must contain "
                                            f"'{prop.retrieval_expression}'", task, e)
            if prop.name in current_props and \
                new_val != updated_props[prop.name]:
                raise WorkflowTaskException("Unable to accept the BPMN message. "
                                            "The payload does not match. Expected "
                                            f"'{prop.retrieval_expression}' to equal "
                                            f"{current_props[prop.name]}.", task)
            else:
                updated_props[prop.name] = new_val
        return updated_props

    def waiting_events(self):
        # Ultimately I'd like to add an event class so that EventDefinitions would not so double duty as both specs
        # and instantiations, and this method would return that.  However, I think that's beyond the scope of the
        # current request.
        events = []
        for task in [t for t in self.get_waiting_tasks() if isinstance(t.task_spec, CatchingEvent)]:
            event_definition = task.task_spec.event_definition
            value = None
            if isinstance(event_definition, TimerEventDefinition):
                value = event_definition.timer_value(task)
            elif isinstance(event_definition, MessageEventDefinition):
                value = event_definition.correlation_properties
            events.append({
                'event_type': event_definition.description,
                'name': event_definition.name if isinstance(event_definition, NamedEventDefinition) else None,
                'value': value
            })
        return events

    def do_engine_steps(self, exit_at = None, will_complete_task=None, did_complete_task=None):
        """
        Execute any READY tasks that are engine specific (for example, gateways
        or script tasks). This is done in a loop, so it will keep completing
        those tasks until there are only READY User tasks, or WAITING tasks
        left.

        :param exit_at: After executing a task with a name matching this param return the task object
        :param will_complete_task: Callback that will be called prior to completing a task
        :param did_complete_task: Callback that will be called after completing a task
        """
        engine_steps = list([t for t in self.get_tasks(TaskState.READY) if not t.task_spec.manual])
        while engine_steps:
            for task in engine_steps:
                if will_complete_task is not None:
                    will_complete_task(task)
                task.run()
                if did_complete_task is not None:
                    did_complete_task(task)
                if task.task_spec.name == exit_at:
                    return task
            engine_steps = list([t for t in self.get_tasks(TaskState.READY) if not t.task_spec.manual])

    def refresh_waiting_tasks(self,
        will_refresh_task=None,
        did_refresh_task=None):
        """
        Refresh the state of all WAITING tasks. This will, for example, update
        Catching Timer Events whose waiting time has passed.

        :param will_refresh_task: Callback that will be called prior to refreshing a task
        :param did_refresh_task: Callback that will be called after refreshing a task
        """
        for my_task in self.get_tasks(TaskState.WAITING):
            if will_refresh_task is not None:
                will_refresh_task(my_task)
            # This seems redundant, but the state could have been updated by another waiting task and no longer be waiting.
            # Someday, I would like to get rid of this method, and also do_engine_steps
            if my_task.state == TaskState.WAITING:
                my_task.task_spec._update(my_task)
            if did_refresh_task is not None:
                did_refresh_task(my_task)

    def get_tasks_from_spec_name(self, name, workflow=None):
        return [t for t in self.get_tasks(workflow=workflow) if t.task_spec.name == name]

    def get_tasks(self, state=TaskState.ANY_MASK, workflow=None):
        # Now that I've revisited and had to ask myself what the hell was I doing, I realize I should comment this
        tasks = []
        top = self._get_outermost_workflow()
        # I think it makes more sense to start with the current workflow, which is probably going to be the top
        # most of the time anyway
        wf = workflow or self
        # We can't filter the iterator on the state because we have to subprocesses, and the subprocess task will
        # almost surely be in a different state than the tasks we want
        for task in Workflow.get_tasks_iterator(wf):
            subprocess = top.subprocesses.get(task.id)
            if task._has_state(state):
                tasks.append(task)
            if subprocess is not None:
                tasks.extend(subprocess.get_tasks(state, subprocess))
        return tasks

    def get_task_from_id(self, task_id, workflow=None):
        for task in self.get_tasks(workflow=workflow):
            if task.id == task_id:
                return task
        raise TaskNotFoundException(f'A task with the given task_id ({task_id}) was not found', task_spec=self.spec)

    def get_ready_user_tasks(self, lane=None, workflow=None):
        """Returns a list of User Tasks that are READY for user action"""
        if lane is not None:
            return [t for t in self.get_tasks(TaskState.READY, workflow) 
                        if t.task_spec.manual and t.task_spec.lane == lane]
        else:
            return [t for t in self.get_tasks(TaskState.READY, workflow) if t.task_spec.manual]

    def get_waiting_tasks(self, workflow=None):
        """Returns a list of all WAITING tasks"""
        return self.get_tasks(TaskState.WAITING, workflow)

    def get_catching_tasks(self, workflow=None):
        return [task for task in self.get_tasks(workflow=workflow) if isinstance(task.task_spec, CatchingEvent)]

    def reset_from_task_id(self, task_id, data=None):
        """Override method from base class, and assures that if the task
        being reset has a boundary event parent, we reset that parent and
        run it rather than resetting to the current task.  This assures
        our boundary events are set to the correct state."""

        task = self.get_task_from_id(task_id)
        run_task_at_end = False

        if isinstance(task.parent.task_spec, _BoundaryEventParent):
            task = task.parent
            run_task_at_end = True # we jumped up one level, so exectute so we are on the correct task as requested.

        descendants = super().reset_from_task_id(task_id, data)
        descendant_ids = [t.id for t in descendants]
        top = self._get_outermost_workflow()

        delete, reset = [], []
        for sp_id, sp in top.subprocesses.items():
            if sp_id in descendant_ids:
                delete.append(sp_id)
                delete.extend([t.id for t in sp.get_tasks() if t.id in top.subprocesses])
            if task in sp.get_tasks():
                reset.append(sp_id)

        # Remove any subprocesses for removed tasks
        for sp_id in delete:
            del top.subprocesses[sp_id]

        # Reset any containing subprocesses
        for sp_id in reset:
            descendants.extend(self.reset_from_task_id(sp_id))
            sp_task = self.get_task_from_id(sp_id)
            sp_task.state = TaskState.WAITING

        if run_task_at_end:
            task.run()

        return descendants

    def cancel(self, workflow=None):

        wf = workflow or self
        cancelled = Workflow.cancel(wf)
        cancelled_ids = [t.id for t in cancelled]
        top = self._get_outermost_workflow()
        to_cancel = []
        for sp_id, sp in top.subprocesses.items():
            if sp_id in cancelled_ids:
                to_cancel.append(sp)
        
        for sp in to_cancel:
            cancelled.extend(self.cancel(sp))

        return cancelled
