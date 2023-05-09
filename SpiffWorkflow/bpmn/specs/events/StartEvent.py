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

from .event_types import CatchingEvent
from ....task import TaskState


class StartEvent(CatchingEvent):
    """Task Spec for a bpmn:startEvent node with an optional event definition."""

    def __init__(self, wf_spec, name, event_definition, **kwargs):
        super(StartEvent, self).__init__(wf_spec, name, event_definition, **kwargs)

    @property
    def spec_type(self):
        return f'{self.event_definition.event_type} Start Event'

    def catch(self, my_task, event_definition):
        # We might need to revisit a start event after it completes or
        # if it got cancelled so we'll still catch messages even if we're finished
        if my_task.state == TaskState.COMPLETED or my_task.state == TaskState.CANCELLED:
            my_task.workflow.reset_from_task_id(my_task.id)
        super(StartEvent, self).catch(my_task, event_definition)
