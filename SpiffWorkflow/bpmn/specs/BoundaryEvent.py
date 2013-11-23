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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.bpmn.specs.IntermediateCatchEvent import IntermediateCatchEvent

class _BoundaryEventParent(BpmnSpecMixin):

    def __init__(self, parent, name, main_child_task_spec, lane=None, **kwargs):
        super(_BoundaryEventParent, self).__init__(parent, name, lane=lane, **kwargs)
        self.main_child_task_spec = main_child_task_spec

    def _child_complete_hook(self, child_task):
        if child_task.task_spec == self.main_child_task_spec or self._should_cancel(child_task.task_spec):
            for sibling in child_task.parent.children:
                if sibling != child_task:
                    if sibling.task_spec == self.main_child_task_spec or (isinstance(sibling.task_spec, BoundaryEvent) and not sibling._is_finished()):
                        sibling.cancel()
            for t in child_task.workflow._get_waiting_tasks():
                t.task_spec._update_state(t)

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
        return issubclass(task_spec.__class__, BoundaryEvent) and task_spec._cancel_activity

class BoundaryEvent(IntermediateCatchEvent):
    """
    Task Spec for a bpmn:boundaryEvent node.
    """

    def __init__(self, parent, name, cancel_activity=None, event_definition=None, **kwargs):
        """
        Constructor.

        :param cancel_activity: True if this is a Cancelling boundary event.
        """
        super(BoundaryEvent, self).__init__(parent, name, event_definition=event_definition, **kwargs)
        self._cancel_activity = cancel_activity
