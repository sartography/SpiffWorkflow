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
from ...bpmn.specs.StartEvent import StartEvent
from ...specs.StartTask import StartTask

class IntermediateCatchEvent(Simple, BpmnSpecMixin):

    """
    Task Spec for a bpmn:intermediateCatchEvent node.
    """

    def __init__(self, wf_spec, name, event_definition=None, **kwargs):
        """
        Constructor.

        :param event_definition: the EventDefinition that we must wait for.
        """
        super(IntermediateCatchEvent, self).__init__(wf_spec, name, **kwargs)
        self.event_definition = event_definition

    def _update_hook(self, my_task):
        target_state = getattr(my_task, '_bpmn_load_target_state', None)
        message = self.event_definition._message_ready(my_task)
        if message:
            if message[1] != None:
                resultVar = message[1]
            else:
                resultVar = my_task.task_spec.name + '_Response'
            my_task.data[resultVar] = message[0]
            # this next line actually matters for some start events.
            my_task.children = []
            my_task._sync_children(my_task.task_spec.outputs)
            super(IntermediateCatchEvent, self)._update_hook(my_task)
        elif (my_task.internal_data.get('repeat', 0) > 0) :
            fired = self.event_definition.has_fired(my_task)
            repeat = my_task.internal_data.get('repeat', 0)
            repeat_count = my_task.internal_data.get('repeat_count', 0)
            if (repeat >= repeat_count) and fired:
                my_task.children = []
                my_task._sync_children(my_task.task_spec.outputs)
                super(IntermediateCatchEvent, self)._update_hook(my_task)
                my_task.workflow.do_engine_steps()
                my_task._set_state(Task.WAITING)
                if not my_task.workflow._is_busy_with_restore():
                    self.entering_waiting_state(my_task)
        elif target_state == Task.READY or (
                not my_task.workflow._is_busy_with_restore() and
                self.event_definition.has_fired(my_task)):
            super(IntermediateCatchEvent, self)._update_hook(my_task)
        else:
            if not my_task.parent._is_finished():
                return
            if not my_task.state == Task.WAITING:
                my_task._set_state(Task.WAITING)
                if not my_task.workflow._is_busy_with_restore():
                    self.entering_waiting_state(my_task)

    def _on_ready_hook(self, my_task):
        self._predict(my_task)

    def _on_complete_hook(self, my_task):
        super(IntermediateCatchEvent, self)._on_complete_hook(my_task)
        if  isinstance(my_task.parent.task_spec, StartTask):
            my_task._set_state(Task.WAITING)


    def accept_message(self, my_task, message):
        if (my_task.state == Task.WAITING and
                self.event_definition._accept_message(my_task, message)):
            self._update(my_task)
            return True
        return False

    def serialize(self, serializer):
        return serializer.serialize_generic_event(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_generic_event(wf_spec, s_state,IntermediateCatchEvent)


