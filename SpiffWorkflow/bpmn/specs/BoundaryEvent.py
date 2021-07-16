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

from ...task import Task
from .BpmnSpecMixin import BpmnSpecMixin
from .IntermediateCatchEvent import IntermediateCatchEvent


class _BoundaryEventParent(BpmnSpecMixin):

    def __init__(self, wf_spec, name, main_child_task_spec, lane=None,
                 **kwargs):
        super(_BoundaryEventParent, self).__init__(
            wf_spec, name, lane=lane, **kwargs)
        self.main_child_task_spec = main_child_task_spec

    def _child_complete_hook(self, child_task):
        if (child_task.task_spec == self.main_child_task_spec or
                self._should_cancel(child_task.task_spec)):
            for sibling in child_task.parent.children:
                if sibling != child_task:
                    if (sibling.task_spec == self.main_child_task_spec or
                        (isinstance(sibling.task_spec, BoundaryEvent)
                         and not sibling._is_finished())):
                        sibling.cancel()
            for t in child_task.workflow._get_waiting_tasks():
                t.task_spec._update(t)

    def _predict_hook(self, my_task):
        # We default to MAYBE
        # for all it's outputs except the main child, which is
        # FUTURE, if my task is definite, otherwise, my own state.
        my_task._sync_children(self.outputs, state=Task.MAYBE)

        if my_task._is_definite():
            state = Task.FUTURE
        else:
            state = my_task.state

        for child in my_task.children:
            if child.task_spec == self.main_child_task_spec:
                child._set_state(state)

    def _should_cancel(self, task_spec):
        return (issubclass(task_spec.__class__, BoundaryEvent) and
                task_spec._cancel_activity)

    def serialize(self, serializer):
        return serializer.serialize_boundary_event_parent(self)
    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_boundary_event_parent(wf_spec, s_state, _BoundaryEventParent)


class BoundaryEvent(IntermediateCatchEvent):
    """
    Task Spec for a bpmn:boundaryEvent node.
    """

    def __init__(self, wf_spec, name, cancel_activity=None,
                 event_definition=None, **kwargs):
        """
        Constructor.

        :param cancel_activity: True if this is a Cancelling boundary event.
        """
        super(BoundaryEvent, self).__init__(
            wf_spec, name, event_definition=event_definition, **kwargs)
        self._cancel_activity = cancel_activity

    def accept_message(self, my_task, message):
        ret = super(BoundaryEvent, self).accept_message(my_task, message)
        # after accepting message this node will be in READY state but
        # if for some reason the task we are attached to gets to COMPLETE
        # state before us then our _BoundaryEventParent will cancel()
        # this node along with all the other siblings
        #
        # to prevent this we complete() this task because _BoundaryEventParent
        # only cancels unfinished children
        if ret and my_task._has_state(Task.READY):
            my_task.complete()
        return ret

    def serialize(self, serializer):
        return serializer.serialize_boundary_event(self)
    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_boundary_event(wf_spec, s_state, BoundaryEvent)
