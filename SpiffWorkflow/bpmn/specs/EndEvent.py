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

from .BpmnSpecMixin import BpmnSpecMixin
from ...specs.Simple import Simple
from ...task import Task


class EndEvent(Simple, BpmnSpecMixin):

    """
    Task Spec for a bpmn:endEvent node.

    From the specification of BPMN (http://www.omg.org/spec/BPMN/2.0/PDF - document number:formal/2011-01-03):
    For a "terminate" End Event, the Process is abnormally terminated - no other ongoing Process instances are
    affected.

    For all other End Events, the behavior associated with the Event type is performed, e.g., the associated Message is
    sent for a Message End Event, the associated signal is sent for a Signal End Event, and so on. The Process
    instance is then completed, if and only if the following two conditions hold:
     * All start nodes of the Process have been visited. More precisely, all Start Events have been triggered, and for all
    starting Event-Based Gateways, one of the associated Events has been triggered.
     * There is no token remaining within the Process instance.
    """

    def __init__(self, wf_spec, name, is_terminate_event=False, **kwargs):
        """
        Constructor.

        :param is_terminate_event: True if this is a terminating end event
        """
        super(EndEvent, self).__init__(wf_spec, name, **kwargs)
        self.is_terminate_event = is_terminate_event

    def _on_complete_hook(self, my_task):
        if self.is_terminate_event:
            # Cancel other branches in this workflow:
            for active_task in my_task.workflow.get_tasks(Task.READY | Task.WAITING):
                if active_task.task_spec == my_task.workflow.spec.end:
                    continue
                elif active_task.workflow == my_task.workflow:
                    active_task.cancel()
                else:
                    active_task.workflow.cancel()
                    for start_sibling in active_task.workflow.task_tree.children[0].parent.children:
                        if not start_sibling._is_finished():
                            start_sibling.cancel()

            my_task.workflow.refresh_waiting_tasks()

        super(EndEvent, self)._on_complete_hook(my_task)
