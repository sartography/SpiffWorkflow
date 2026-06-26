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

from SpiffWorkflow import TaskState
from SpiffWorkflow.specs import WorkflowSpec, MultiChoice
from SpiffWorkflow.util.deep_merge import DeepMerge
from SpiffWorkflow.bpmn.specs.control import _EndJoin, BpmnStartTask, SimpleBpmnTask
from SpiffWorkflow.bpmn.specs.mixins.events.start_event import StartEvent
from SpiffWorkflow.bpmn.specs.mixins.multiinstance_task import StandardLoopTask, MultiInstanceTask


class BpmnProcessSpec(WorkflowSpec):
    """
    This class represents the specification of a BPMN process workflow. This
    specialises the standard Spiff WorkflowSpec class with a few extra methods
    and attributes.
    """

    def __init__(self, name=None, description=None, filename=None, svg=None):
        """
        Constructor.

        :param svg: This provides the SVG representation of the workflow as an
        LXML node. (optional)
        """
        super().__init__(name=name, filename=filename)
        self.start = BpmnStartTask(self, 'Start')
        self.end = _EndJoin(self, '%s.EndJoin' % (self.name))
        self.end.connect(SimpleBpmnTask(self, 'End'))
        self.svg = svg
        self.description = description
        self.io_specification = None
        self.data_objects = {}
        self.data_stores = {}
        self.correlation_keys = {}
        self.bpmn_start_events = []

    def _add_notify(self, task_spec):
        super()._add_notify(task_spec)
        if isinstance(task_spec, (StartEvent, )):
            self.bpmn_start_events.append(task_spec)


class AdHocSubprocessSpec(BpmnProcessSpec):
    """
    This class represents an Ad Hoc Subprocess.  Everything about it is questionable.  I 
    think even the BPMN authors were skeptical about it.

    But there is a demand for this, so I'm taking a stab at implementation.

    If a task has no inputs, it will be connected to the start spec and run at least once.
    A task can be run more than once if it is of a type that is conditionally executed.
    Whenever a task completes, it can be reexecuted if it completed and the condition is
    not met.

    Execution is pretty clearly determined by the state of the data, which is more or less
    wholly incompatible with reliance on task data, since tasks can't be connected to each
    other in any meaningful way.  Therefore, I'm relying on workflow data to maintain the
    state.
    """

    def __init__(self, completion_condition=None, parallel=True, cancel_remaining=True, **kwargs):
        super().__init__(**kwargs)
        self.completion_condition = completion_condition
        self.parallel = parallel
        self.cancel_remaining = cancel_remaining
        self.conditional_paths = []

    def create_paths(self):
        # This forces the conditions to be checked at the start of the workflow
        self.start.completed_event.connect(self.path_complete)
        for task_spec in self.task_specs.values():
            if isinstance(task_spec, (BpmnStartTask, _EndJoin, SimpleBpmnTask)):
                continue
            if len(task_spec.inputs) == 0:
                if self.conditional_path(task_spec):
                    self.conditional_paths.append(task_spec)
                else:
                    self.start.connect(task_spec)
            if len(task_spec.outputs) == 0:
                task_spec.connect(self.end)
                task_spec.completed_event.connect(self.path_complete)

    def path_complete(self, workflow, task):

        workflow.data.update(**task.data)
        if workflow.script_engine.environment.evaluate(self.completion_condition, workflow.data):
            if self.cancel_remaining:
                for active_task in workflow.get_tasks(state=TaskState.NOT_FINISHED_MASK):
                    if active_task.task_spec.name not in [self.end.name, 'End']:
                        active_task.cancel()
        else:
            active_branches = []
            for child in workflow.task_tree.children:
                # Updating loop/multiinstance data mid-execution is likely to lead to very bad results
                # For other tasks, I think we can safely update it (though it might not have an effect in some cases)
                active_task = workflow.get_next_task(child, state=TaskState.NOT_FINISHED_MASK)
                if active_task is None or active_task.task_spec.name == self.end.name:
                    continue
                if not isinstance(active_task.task_spec, (MultiChoice, StandardLoopTask, MultiInstanceTask)):
                    DeepMerge.merge(active_task.data, workflow.data)
                    active_task.data.pop('data_objects')
                if child.task_spec in self.conditional_paths:
                    active_branches.append(child.task_spec)

            for task_spec in self.conditional_paths:
                # Start any conditional branches that are not already running.
                if task_spec not in active_branches:
                    self.add_path(workflow, task_spec)

    def add_path(self, workflow, task_spec):

        trigger = False
        if isinstance(task_spec, (MultiChoice, )):
            for cond, output in task_spec.cond_task_specs:
                if cond is None or self.check_condition(cond.args[0], workflow):
                    trigger = True
                    break
        elif isinstance(task_spec, (StandardLoopTask, )):
            # Loops run while the condition is true, so if the condition is true, I'll restart the task
            trigger = task_spec.condition is not None and self.check_condition(task_spec.condition, workflow)
        elif isinstance(task_spec, (MultiInstanceTask, )):
            # Multiinstance tasks run until the condition is true, so I'll restart if it *isn't*.
            # I really don't understand why the spec authors couldn't have made the semantics consistent here.
            trigger = task_spec.condition is not None and not self.check_condition(task_spec.condition, workflow)

        if trigger:
            if self.start not in task_spec.inputs:
                self.start.connect(task_spec)
            child = workflow.task_tree._add_child(task_spec, TaskState.READY)
            child.triggered = True
            task_spec._predict(child, mask=TaskState.NOT_FINISHED_MASK)
            DeepMerge.merge(child.data, workflow.data)
            child.data.pop('data_objects')

    def conditional_path(self, task_spec):
        return (
            isinstance(task_spec, (MultiChoice, )) or 
            (isinstance(task_spec, (StandardLoopTask, MultiInstanceTask)) and task_spec.condition is not None)
        )

    def check_condition(self, cond, workflow):
        return workflow.script_engine.environment.evaluate(cond, workflow.data, external_context=workflow.data_objects)
