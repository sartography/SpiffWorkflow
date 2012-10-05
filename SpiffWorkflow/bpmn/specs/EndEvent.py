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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.bpmn.specs.ParallelGateway import ParallelGateway
from SpiffWorkflow.Task import Task

class EndEvent(ParallelGateway, BpmnSpecMixin):
    """
    Task Spec for a bpmn:endEvent node.
    """

    def __init__(self, parent, name, is_terminate_event=False, **kwargs):
        """
        Constructor.

        :param is_terminate_event: True if this is a terminating end event
        """
        super(EndEvent, self).__init__(parent, name, **kwargs)
        self.is_terminate_event = is_terminate_event

    def _on_complete_hook(self, my_task):
        if self.is_terminate_event:
            #Cancel other branches in this workflow:
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