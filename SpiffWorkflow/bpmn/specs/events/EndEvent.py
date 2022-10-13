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

from .event_types import ThrowingEvent
from .event_definitions import TerminateEventDefinition, CancelEventDefinition
from ....task import TaskState


class EndEvent(ThrowingEvent):
    """
    Task Spec for a bpmn:endEvent node.

    From the specification of BPMN (http://www.omg.org/spec/BPMN/2.0/PDF -
    document number:formal/2011-01-03): For a "terminate" End Event, the
    Process is abnormally terminated - no other ongoing Process instances are
    affected.

    For all other End Events, the behavior associated with the Event type is
    performed, e.g., the associated Message is sent for a Message End Event,
    the associated signal is sent for a Signal End Event, and so on. The
    Process instance is then completed, if and only if the following two
    conditions hold:
     * All start nodes of the Process have been visited. More precisely, all
       Start Events have been triggered, and for all starting Event-Based
       Gateways, one of the associated Events has been triggered.
     * There is no token remaining within the Process instance.
    """

    def __init__(self, wf_spec, name, event_definition, **kwargs):
        super(EndEvent, self).__init__(wf_spec, name, event_definition, **kwargs)

    @property
    def spec_type(self):
        return 'End Event'

    def _on_complete_hook(self, my_task):

        super(EndEvent, self)._on_complete_hook(my_task)

        if isinstance(self.event_definition, TerminateEventDefinition):

            # We are finished.  Set the workflow data and cancel all tasks
            my_task.workflow.set_data(**my_task.data)
            for task in my_task.workflow.get_tasks(TaskState.NOT_FINISHED_MASK, workflow=my_task.workflow):
                task.cancel()

        elif isinstance(self.event_definition, CancelEventDefinition):
            my_task.workflow.cancel()

    def serialize(self, serializer):
        return serializer.serialize_generic_event(self)

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state):
        return serializer.deserialize_generic_event(wf_spec, s_state, EndEvent)
