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

import warnings

from SpiffWorkflow.task import Task
from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.exceptions import WorkflowException

from SpiffWorkflow.bpmn.specs.control import BoundaryEventSplit
from SpiffWorkflow.bpmn.specs.event_definitions.timer import TimerEventDefinition

from SpiffWorkflow.bpmn.util.subworkflow import BpmnBaseWorkflow, BpmnSubWorkflow
from SpiffWorkflow.bpmn.util.event import EventManager

from .script_engine.python_engine import PythonScriptEngine


class BpmnWorkflow(BpmnBaseWorkflow):
    """
    The engine that executes a BPMN workflow. This specialises the standard
    Spiff Workflow class with a few extra methods and attributes.
    """

    def __init__(self, spec, subprocess_specs=None, script_engine=None, **kwargs):
        """
        Constructor.

        :param script_engine: set to an extension of PythonScriptEngine if you
        need a specialised version. Defaults to the script engine of the top
        most workflow, or to the PythonScriptEngine if none is provided.
        """
        self.subprocess_specs = subprocess_specs or {}
        self.subprocesses = {}
        self.bpmn_events = []
        self.correlations = {}
        self.event_manager = EventManager(self)
        super().__init__(spec, **kwargs)

        for obj in self.spec.data_objects:
            self.data['data_objects'][obj] = None
        self.__script_engine = script_engine or PythonScriptEngine()

    @property
    def script_engine(self):
        return self.__script_engine

    @script_engine.setter
    def script_engine(self, engine):
        self.__script_engine = engine

    @property
    def top_workflow(self):
        return self

    @property
    def parent_task_id(self):
        return None
    
    @property
    def parent_workflow(self):
        return None
    
    @property
    def depth(self):
        return 0

    def create_subprocess(self, my_task, spec_name):
        # This creates a subprocess for an existing task
        subprocess = BpmnSubWorkflow(
            self.subprocess_specs[spec_name],
            parent_task_id=my_task.id,
            top_workflow=self)
        self.subprocesses[my_task.id] = subprocess
        return subprocess

    def get_subprocess(self, my_task):
        return self.subprocesses.get(my_task.id)

    def delete_subprocess(self, my_task):
        subprocess = self.subprocesses.get(my_task.id)
        tasks = subprocess.get_tasks()
        for sp in [c for c in self.subprocesses.values() if c.parent_workflow == subprocess]:
            tasks.extend(self.delete_subprocess(self.get_task_from_id(sp.parent_task_id)))
        del self.subprocesses[my_task.id]
        return tasks

    def get_active_subprocesses(self):
        return [sp for sp in self.subprocesses.values() if not sp.completed]

    def catch(self, event):
        self.event_manager.catch(event)

    def send_event(self, event):
        """Allows this workflow to catch an externally generated event."""

        if self.event_manager.catch(event, internal=False) == 0:
            raise WorkflowException(f"This process is not waiting for {event.event_definition.name}")

    def get_events(self):
        """Returns the list of events that cannot be handled from within this workflow."""
        events = self.bpmn_events
        self.bpmn_events = []
        return events

    def waiting_events(self):
        return self.event_manager.get_waiting_tasks()

    def do_engine_steps(self, will_complete_task=None, did_complete_task=None):
        """
        Execute any READY tasks that are engine specific (for example, gateways
        or script tasks). This is done in a loop, so it will keep completing
        those tasks until there are only READY User tasks, or WAITING tasks
        left.

        :param will_complete_task: Callback that will be called prior to completing a task
        :param did_complete_task: Callback that will be called after completing a task
        """
        count = self._do_engine_steps(will_complete_task, did_complete_task)
        while count > 0:
            count = self._do_engine_steps(will_complete_task, did_complete_task)
        self.refresh_timers()

    def _do_engine_steps(self, will_complete_task=None, did_complete_task=None):

        def update_workflow(wf):
            count = 0
            # Wanted to use the iterator method here, but at least this is a shorter list
            for task in wf.get_tasks(state=TaskState.READY):
                if not task.task_spec.manual:
                    if will_complete_task is not None:
                        will_complete_task(task)
                    task.run()
                    count += 1
                    if did_complete_task is not None:
                        did_complete_task(task)
            return count

        active_subprocesses = self.get_active_subprocesses()
        for subprocess in sorted(active_subprocesses, key=lambda v: v.depth, reverse=True):
            count = None
            while count is None or count > 0:
                count = update_workflow(subprocess)
            if subprocess.parent_task_id is not None:
                task = self.get_task_from_id(subprocess.parent_task_id)
                task.task_spec._update(task)

        count = update_workflow(self)
        return count > 0 or len(self.get_active_subprocesses()) > len(active_subprocesses)

    def refresh_waiting_tasks(self, will_refresh_task=None, did_refresh_task=None):
        """
        Refresh the state of all WAITING tasks. This will, for example, update
        Catching Timer Events whose waiting time has passed.

        :param will_refresh_task: Callback that will be called prior to refreshing a task
        :param did_refresh_task: Callback that will be called after refreshing a task
        """
        warnings.warn(
            DeprecationWarning(f'BpmnWorkflow.refresh_waiting_tasks will be removed in future versions; use refresh_timers')
        )
        self.refresh_timers()

    def refresh_timers(self):
        # Ideally this would go in event manager but I can't import the necessary classes there
        # Eventually I'll move it
        for task in list(self.event_manager.tasks.values()):
            if isinstance(task.task_spec.event_definition, (TimerEventDefinition, )):
                task.task_spec._update(task)

    def get_task_from_id(self, task_id):
        if task_id not in self.tasks:
            for subprocess in self.subprocesses.values():
                task = subprocess.get_task_from_id(task_id)
                if task is not None:
                    return task
        return super().get_task_from_id(task_id)

    def reset_from_task_id(self, task_id, data=None, remove_subprocess=True):

        task = self.get_task_from_id(task_id)
        # Since recursive deletion of subprocesses requires access to the tasks, we have to delete any subprocesses first
        # We also need diffeent behavior for the case where we explictly reset to a subprocess (in which case we delete it)
        # vs resetting inside (where we leave it and reset the tasks that descend from it)
        descendants = []

        # If we're resetting to a boundary event, we also have to delete subprocesses underneath the attached events
        top = task if not isinstance(task.parent.task_spec, BoundaryEventSplit) else task.parent
        for desc in filter(lambda t: t.id in self.subprocesses, top):
            if desc != task or remove_subprocess:
                descendants.extend(self.delete_subprocess(desc))

        # This resets the boundary event branches
        if isinstance(task.parent.task_spec, BoundaryEventSplit):
            for child in task.parent.children:
                descendants.extend(super().reset_from_task_id(child.id, data if child == task else None))
        else:
            descendants.extend(super().reset_from_task_id(task.id, data))

        if task.workflow.parent_task_id is not None:
            sp_task = self.get_task_from_id(task.workflow.parent_task_id)
            descendants.extend(self.reset_from_task_id(sp_task.id, remove_subprocess=False))
            sp_task._set_state(TaskState.STARTED)

        return descendants

    def cancel(self, workflow=None):

        wf = workflow or self
        cancelled = BpmnBaseWorkflow.cancel(wf)
        cancelled_ids = [t.id for t in cancelled]
        to_cancel = []
        for sp_id, sp in self.subprocesses.items():
            if sp_id in cancelled_ids:
                to_cancel.append(sp)

        for sp in to_cancel:
            cancelled.extend(self.cancel(sp))

        return cancelled


