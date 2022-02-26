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

from .event_definitions import NoneEventDefinition, MessageEventDefinition, CycleTimerEventDefinition
from ..BpmnSpecMixin import BpmnSpecMixin
from ....specs.Simple import Simple
from ....specs.StartTask import StartTask
from ....task import Task

class CatchingEvent(Simple, BpmnSpecMixin):
    """Base Task Spec for Catching Event nodes."""

    def __init__(self, wf_spec, name, event_definition, **kwargs):
        """
        Constructor.

        :param event_definition: the EventDefinition that we must wait for.
        """
        super(CatchingEvent, self).__init__(wf_spec, name, **kwargs)
        self.event_definition = event_definition

    def catches(self, my_task, event_definition):
        return self.event_definition == event_definition

    def catch(self, my_task, event_definition):
        """
        Catch is called by the workflow when the task has matched an event
        definition, at which point we can update our task's state.
        """
        self.event_definition.catch(my_task, event_definition)
        self._update_hook(my_task)

    def _update_hook(self, my_task):

        if my_task.state == Task.WAITING and self.event_definition.has_fired(my_task):
            my_task._ready()
        super(CatchingEvent, self)._update_hook(my_task)

    def _on_ready(self, my_task):

        # None events don't propogate, so as soon as we're ready, we fire our event
        if isinstance(self.event_definition, NoneEventDefinition):
            my_task._set_internal_data(event_fired=True)

        # If we have not seen the event we're waiting for, enter the waiting state
        if not self.event_definition.has_fired(my_task):
            my_task._set_state(Task.WAITING)
        super(CatchingEvent, self)._on_ready(my_task)

    def _on_complete_hook(self, my_task):

        if isinstance(self.event_definition, MessageEventDefinition):
            # If we are a message event, then we need to copy the event data out of
            # our internal data and into the task data
            result_var, result = my_task.internal_data[self.event_definition.name]
            my_task.data[result_var] = result
        self.event_definition.reset(my_task)
        super(CatchingEvent, self)._on_complete_hook(my_task)

    def serialize(self, serializer):
        return serializer.serialize_generic_event(self)

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state):
        return serializer.deserialize_generic_event(wf_spec, s_state, cls)


class ThrowingEvent(Simple, BpmnSpecMixin):
    """Base Task Spec for Throwing Event nodes."""

    def __init__(self, wf_spec, name, event_definition, **kwargs):
        """
        Constructor.

        :param event_definition: the EventDefinition to be thrown.
        """
        super(ThrowingEvent, self).__init__(wf_spec, name, **kwargs)
        self.event_definition = event_definition

    def _on_complete_hook(self, my_task):
        super(ThrowingEvent, self)._on_complete_hook(my_task)
        self.event_definition.throw(my_task)

    def serialize(self, serializer):
        return serializer.serialize_generic_event(self)

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state):
        return serializer.deserialize_generic_event(wf_spec, s_state, cls)
