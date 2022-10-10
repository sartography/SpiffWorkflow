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

from .event_types import ThrowingEvent, CatchingEvent
from .event_definitions import CycleTimerEventDefinition
from ..BpmnSpecMixin import BpmnSpecMixin
from ....specs.Simple import Simple
from ....task import TaskState

class SendTask(ThrowingEvent):

    @property
    def spec_type(self):
        return 'Send Task'


class ReceiveTask(CatchingEvent):

    @property
    def spec_type(self):
        return 'Receive Task'


class IntermediateCatchEvent(CatchingEvent):

    @property
    def spec_type(self):
        return f'{self.event_definition.event_type} Catching Event'


class IntermediateThrowEvent(ThrowingEvent):

    @property
    def spec_type(self):
        return f'{self.event_definition.event_type} Throwing Event'


class _BoundaryEventParent(Simple, BpmnSpecMixin):
    """This task is inserted before a task with boundary events."""

    # I wonder if this would be better modelled as some type of join.
    # It would make more sense to have the boundary events and the task
    # they're attached to be inputs rather than outputs.

    def __init__(self, wf_spec, name, main_child_task_spec, **kwargs):

        super(_BoundaryEventParent, self).__init__(wf_spec, name)
        self.main_child_task_spec = main_child_task_spec

    @property
    def spec_type(self):
        return 'Boundary Event Parent'

    def _on_ready_hook(self, my_task):

        # Clear any events that our children might have received and
        # wait for new events
        for child in my_task.children:
            if isinstance(child.task_spec, BoundaryEvent):
                child.task_spec.event_definition.reset(child)
                child._set_state(TaskState.WAITING)

    def _child_complete_hook(self, child_task):

        # If the main child completes, or a cancelling event occurs, cancel any
        # unfinished children
        if child_task.task_spec == self.main_child_task_spec or child_task.task_spec.cancel_activity:
            for sibling in child_task.parent.children:
                if sibling == child_task:
                    continue
                if sibling.task_spec == self.main_child_task_spec or not sibling._is_finished():
                    sibling.cancel()
            for t in child_task.workflow._get_waiting_tasks():
                t.task_spec._update(t)

        # If our event is a cycle timer, we need to set it back to waiting so it can fire again
        elif isinstance(child_task.task_spec.event_definition, CycleTimerEventDefinition):
            child_task._set_state(TaskState.WAITING)
            child_task.task_spec._update_hook(child_task)

    def _predict_hook(self, my_task):

        # Events attached to the main task might occur
        my_task._sync_children(self.outputs, state=TaskState.MAYBE)
        # The main child's state is based on this task's state
        state = TaskState.FUTURE if my_task._is_definite() else my_task.state
        for child in my_task.children:
            if child.task_spec == self.main_child_task_spec:
                child._set_state(state)

    def serialize(self, serializer):
        return serializer.serialize_boundary_event_parent(self)

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state):
        return serializer.deserialize_boundary_event_parent(wf_spec, s_state, cls)

class BoundaryEvent(CatchingEvent):
    """Task Spec for a bpmn:boundaryEvent node."""

    def __init__(self, wf_spec, name, event_definition, cancel_activity, **kwargs):
        """
        Constructor.

        :param cancel_activity: True if this is a Cancelling boundary event.
        """
        super(BoundaryEvent, self).__init__(wf_spec, name, event_definition, **kwargs)
        self.cancel_activity = cancel_activity

    @property
    def spec_type(self):
        interrupting = 'Interrupting' if self.cancel_activity else 'Non-Interrupting'
        return f'{interrupting} {self.event_definition.event_type} Event'


    def catches(self, my_task, event_definition, correlations=None):
        # Boundary events should only be caught while waiting
        return super(BoundaryEvent, self).catches(my_task, event_definition, correlations) and my_task.state == TaskState.WAITING

    def catch(self, my_task, event_definition):
        super(BoundaryEvent, self).catch(my_task, event_definition)
        my_task.complete()

    def _on_complete_hook(self, my_task):
        super(BoundaryEvent, self)._on_complete_hook(my_task)
        # Notify the boundary event parent as well.
        my_task.parent.task_spec._child_complete_hook(my_task)

    def serialize(self, serializer):
        return serializer.serialize_boundary_event(self)

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state):
        return serializer.deserialize_boundary_event(wf_spec, s_state, cls)
