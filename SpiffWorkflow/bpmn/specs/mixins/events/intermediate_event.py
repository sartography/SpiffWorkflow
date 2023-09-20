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

from SpiffWorkflow.util.task import TaskState
from .event_types import ThrowingEvent, CatchingEvent


class SendTask(ThrowingEvent):
    pass

class ReceiveTask(CatchingEvent):
    pass

class IntermediateCatchEvent(CatchingEvent):
    pass

class IntermediateThrowEvent(ThrowingEvent):
    pass


class BoundaryEvent(CatchingEvent):
    """Task Spec for a bpmn:boundaryEvent node."""

    def __init__(self, wf_spec, bpmn_id, event_definition, cancel_activity, **kwargs):
        """
        Constructor.

        :param cancel_activity: True if this is a Cancelling boundary event.
        """
        super(BoundaryEvent, self).__init__(wf_spec, bpmn_id, event_definition, **kwargs)
        self.cancel_activity = cancel_activity

    def catches(self, my_task, event):
        # Boundary events should only be caught while waiting
        return my_task.state == TaskState.WAITING and super().catches(my_task, event)


class EventBasedGateway(CatchingEvent):

    def _predict_hook(self, my_task):
        my_task._sync_children(self.outputs, state=TaskState.MAYBE)

    def _on_ready_hook(self, my_task):
        for child in my_task.children:
            if not child.internal_data.get('event_fired'):
                child.cancel()
