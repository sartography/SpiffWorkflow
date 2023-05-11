
# Copyright (C) 2023 Sartography
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

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.specs.StartTask import StartTask
from SpiffWorkflow.bpmn.specs.bpmn_task_spec import BpmnTaskSpec
from SpiffWorkflow.bpmn.specs.mixins.unstructured_join import UnstructuredJoin
from SpiffWorkflow.bpmn.specs.mixins.events.intermediate_event import BoundaryEvent


class BpmnStartTask(BpmnTaskSpec, StartTask):
    pass

class SimpleBpmnTask(BpmnTaskSpec):
    pass

class _BoundaryEventParent(BpmnTaskSpec):
    """This task is inserted before a task with boundary events."""

    # I wonder if this would be better modelled as some type of join.
    # It would make more sense to have the boundary events and the task
    # they're attached to be inputs rather than outputs.

    def __init__(self, wf_spec, name, main_child_task_spec, **kwargs):
        super(_BoundaryEventParent, self).__init__(wf_spec, name, **kwargs)
        self.main_child_task_spec = main_child_task_spec

    @property
    def spec_type(self):
        return 'Boundary Event Parent'

    def _run_hook(self, my_task):
        # Clear any events that our children might have received and wait for new events
        for child in my_task.children:
            if isinstance(child.task_spec, BoundaryEvent):
                child.task_spec.event_definition.reset(child)
                child._set_state(TaskState.WAITING)
        return True

    def _child_complete_hook(self, child_task):
        # If the main child completes, or a cancelling event occurs, cancel any unfinished children
        if child_task.task_spec == self.main_child_task_spec or child_task.task_spec.cancel_activity:
            for sibling in child_task.parent.children:
                if sibling == child_task:
                    continue
                if sibling.task_spec == self.main_child_task_spec or not sibling._is_finished():
                    sibling.cancel()

    def _predict_hook(self, my_task):
        # Events attached to the main task might occur
        my_task._sync_children(self.outputs, state=TaskState.MAYBE)
        # The main child's state is based on this task's state
        state = TaskState.FUTURE if my_task._is_definite() else my_task.state
        for child in my_task.children:
            if child.task_spec == self.main_child_task_spec:
                child._set_state(state)


class _EndJoin(UnstructuredJoin, BpmnTaskSpec):

    def _check_threshold_unstructured(self, my_task, force=False):
        # Look at the tree to find all ready and waiting tasks (excluding
        # ourself). The EndJoin waits for everyone!
        waiting_tasks = []
        for task in my_task.workflow.get_tasks(TaskState.READY | TaskState.WAITING):
            if task.thread_id != my_task.thread_id:
                continue
            if task.task_spec == my_task.task_spec:
                continue

            is_mine = False
            w = task.workflow
            if w == my_task.workflow:
                is_mine = True
            while w and w.outer_workflow != w:
                w = w.outer_workflow
                if w == my_task.workflow:
                    is_mine = True
            if is_mine:
                waiting_tasks.append(task)

        return force or len(waiting_tasks) == 0, waiting_tasks

    def _run_hook(self, my_task):
        result = super(_EndJoin, self)._run_hook(my_task)
        my_task.workflow.data.update(my_task.data)
        return result