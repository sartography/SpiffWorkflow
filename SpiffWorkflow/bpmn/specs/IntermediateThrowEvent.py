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
from ...specs.Simple import Simple


class IntermediateThrowEvent(Simple, BpmnSpecMixin):

    """
    Task Spec for a bpmn:intermediateCatchEvent node.
    """

    def __init__(self, wf_spec, name, event_definition=None, **kwargs):
        """
        Constructor.

        :param event_definition: the EventDefinition that we must wait for.
        """
        super(IntermediateThrowEvent, self).__init__(wf_spec, name, **kwargs)
        self.event_definition = event_definition
        self.name = name

    def _update_hook(self, my_task):
        target_state = getattr(my_task, '_bpmn_load_target_state', None)
        if target_state == Task.READY or (
                not my_task.workflow._is_busy_with_restore() and
                self.event_definition.has_fired(my_task)):
            super(IntermediateThrowEvent, self)._update_hook(my_task)
        else:
            if not my_task.parent._is_finished():
                return
            # here we diverge from the previous
            # and we just send the message
            if hasattr(self.event_definition,'resultVar'):
                self.event_definition._send_message(my_task, self.event_definition.resultVar)
            else:
                self.event_definition._send_message(my_task)
            # if we throw the message, then we need to be completed.
            if not my_task.state == Task.READY:
                my_task._set_state(Task.READY)

    def _on_ready_hook(self, my_task):
        self._predict(my_task)

    def serialize(self, serializer):
        return serializer.serialize_generic_event(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_generic_event(wf_spec, s_state,IntermediateThrowEvent)



