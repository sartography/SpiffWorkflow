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

from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.util.task import TaskState, TaskFilter, TaskIterator
from SpiffWorkflow.specs.StartTask import StartTask
from SpiffWorkflow.specs.Join import Join

from SpiffWorkflow.bpmn.specs.bpmn_task_spec import BpmnTaskSpec
from SpiffWorkflow.bpmn.specs.mixins.unstructured_join import UnstructuredJoin
from SpiffWorkflow.bpmn.specs.mixins.events.intermediate_event import BoundaryEvent
from SpiffWorkflow.bpmn.specs.mixins.events.start_event import StartEvent


class BpmnStartTask(BpmnTaskSpec, StartTask):
    pass

class SimpleBpmnTask(BpmnTaskSpec):
    pass

class EventSplit(SimpleBpmnTask):

    def __init__(self, event_type, wf_spec, name, **kwargs):
        super().__init__(wf_spec, name, **kwargs)
        self.event_type = event_type

    def _predict_hook(self, my_task):
        # Events attached to the main task might occur
        my_task._sync_children(self.outputs, state=TaskState.MAYBE)
        # The main child's state is based on this task's state
        state = TaskState.FUTURE if my_task.has_state(TaskState.DEFINITE_MASK) else my_task.state
        for child in my_task.children:
            if not isinstance(child.task_spec, self.event_type):
                child._set_state(state)

    def _run_hook(self, my_task):
        for task in my_task.children:
            if isinstance(task.task_spec, self.event_type) and task.has_state(TaskState.PREDICTED_MASK):
                task._set_state(TaskState.WAITING)
        return True


class BoundaryEventSplit(EventSplit):
    def __init__(self, wf_spec, name, **kwargs):
        super().__init__(BoundaryEvent, wf_spec, name, **kwargs)


class StartEventSplit(EventSplit):
    def __init__(self, wf_spec, name, **kwargs):
        super().__init__(StartEvent, wf_spec, name, **kwargs)


class BoundaryEventJoin(Join, BpmnTaskSpec):
    """This task is inserted before a task with boundary events."""

    def __init__(self, wf_spec, name, **kwargs):
        super().__init__(wf_spec, name, **kwargs)

    def _check_threshold_structured(self, my_task):
        split_task = my_task.find_ancestor(self.split_task)
        if split_task is None:
            raise WorkflowException(f'Split at {self.split_task} was not reached', task_spec=self)

        main, interrupting, noninterrupting = None, [], []
        for task in split_task.children:
            if not isinstance(task.task_spec, BoundaryEvent):
                main = task
            elif task.task_spec.cancel_activity:
                interrupting.append(task)
            else:
                noninterrupting.append(task)

        if main is None:
            raise WorkflowException(f'No main task found', task_spec=self)

        interrupt = any([t.has_state(TaskState.READY|TaskState.COMPLETED) for t in interrupting])
        finished = main.has_state(TaskState.FINISHED_MASK) or interrupt
        if finished:
            cancel = [t for t in interrupting + noninterrupting if t.state == TaskState.WAITING]
            if interrupt:
                cancel += [main]
        else:
            cancel = []
        return finished, cancel


class StartEventJoin(Join, BpmnTaskSpec):

    def __init__(self, wf_spec, name, **kwargs):
        super().__init__(wf_spec, name, **kwargs)

    def _check_threshold_structured(self, my_task):

        split_task = my_task.find_ancestor(self.split_task)
        if split_task is None:
            raise WorkflowException(f'Split at {self.split_task} was not reached', task_spec=self)

        may_fire, waiting = False, []
        for task in split_task.children:
            if task.state == TaskState.COMPLETED:
                may_fire = True
            else:
                waiting.append(task)
        
        return may_fire, waiting


class _EndJoin(UnstructuredJoin, BpmnTaskSpec):

    def _check_threshold_unstructured(self, my_task):
        # Look at the tree to find all ready and waiting tasks (excluding
        # ourself). The EndJoin waits for everyone!
        for task in TaskIterator(my_task.workflow.task_tree, state=TaskState.READY|TaskState.WAITING, end_at_spec=self.name):
            if task.task_spec == my_task.task_spec:
                continue
            # This method returns waiting tasks so that they can be cancelled on cancelling joins
            # This is not a cancelling join so we can omit building the list and return false as soon as we find any waiting task
            may_fire = False
            break
        else:
            may_fire = True

        return may_fire, []

    def _run_hook(self, my_task):
        result = super(_EndJoin, self)._run_hook(my_task)
        my_task.workflow.data.update(my_task.data)
        return result
