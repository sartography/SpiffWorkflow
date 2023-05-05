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

from SpiffWorkflow.task import TaskState
from .event_types import CatchingEvent


class StartEvent(CatchingEvent):
    """Task Spec for a bpmn:startEvent node with an optional event definition."""

    def catch(self, my_task, event_definition):

        # We might need to revisit a start event after it completes or
        # if it got cancelled so we'll still catch messages even if we're finished
        if my_task.state == TaskState.COMPLETED or my_task.state == TaskState.CANCELLED:
            my_task.set_children_future()
            my_task._set_state(TaskState.WAITING)
        super(StartEvent, self).catch(my_task, event_definition)

