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

from .event_definitions import MessageEventDefinition, NoneEventDefinition, CycleTimerEventDefinition
from ..BpmnSpecMixin import BpmnSpecMixin
from ....specs.Simple import Simple
from ....task import TaskState

class CatchingEvent(Simple, BpmnSpecMixin):
    """Base Task Spec for Catching Event nodes."""

    def __init__(self, wf_spec, name, event_definition, **kwargs):
        """
        Constructor.

        :param event_definition: the EventDefinition that we must wait for.
        """
        super(CatchingEvent, self).__init__(wf_spec, name, **kwargs)
        self.event_definition = event_definition

    def catches(self, my_task, event_definition, correlations=None):
        if self.event_definition == event_definition:
            return all([correlations.get(key) == my_task.workflow.correlations.get(key) for key in correlations ])
        else:
            return False

    def catch(self, my_task, event_definition):
        """
        Catch is called by the workflow when the task has matched an event
        definition, at which point we can update our task's state.
        """
        self.event_definition.catch(my_task, event_definition)
        my_task._set_state(TaskState.WAITING)

    def _update_hook(self, my_task):

        super()._update_hook(my_task)
        # None events don't propogate, so as soon as we're ready, we fire our event
        if isinstance(self.event_definition, NoneEventDefinition):
            my_task._set_internal_data(event_fired=True)

        if self.event_definition.has_fired(my_task):
            return True
        elif isinstance(self.event_definition, CycleTimerEventDefinition):
            if self.event_definition.cycle_complete(my_task):
                for output in self.outputs:
                    child = my_task._add_child(output, TaskState.READY)
                    child.task_spec._predict(child, mask=TaskState.READY|TaskState.PREDICTED_MASK)
                if my_task.state != TaskState.WAITING:
                    my_task._set_state(TaskState.WAITING)
        elif my_task.state != TaskState.WAITING:
            my_task._set_state(TaskState.WAITING)

    def _run_hook(self, my_task):

        if isinstance(self.event_definition, MessageEventDefinition):
            self.event_definition.update_task_data(my_task)
        self.event_definition.reset(my_task)
        return super(CatchingEvent, self)._run_hook(my_task)

    # This fixes the problem of boundary events remaining cancelled if the task is reused.
    # It pains me to add these methods, but unless we can get rid of the loop reset task we're stuck

    def task_should_set_children_future(self, my_task):
        return True

    def task_will_set_children_future(self, my_task):
        my_task.internal_data = {}


class ThrowingEvent(Simple, BpmnSpecMixin):
    """Base Task Spec for Throwing Event nodes."""

    def __init__(self, wf_spec, name, event_definition, **kwargs):
        """
        Constructor.

        :param event_definition: the EventDefinition to be thrown.
        """
        super(ThrowingEvent, self).__init__(wf_spec, name, **kwargs)
        self.event_definition = event_definition

    def _run_hook(self, my_task):
        super(ThrowingEvent, self)._run_hook(my_task)
        self.event_definition.throw(my_task)
        return True
