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
import time
from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.specs.base import TaskSpec

from SpiffWorkflow.bpmn.specs.event_definitions.simple import NoneEventDefinition
from SpiffWorkflow.bpmn.specs.event_definitions.timer import CycleTimerEventDefinition


class CatchingEvent(TaskSpec):
    """Base Task Spec for Catching Event nodes."""

    def __init__(self, wf_spec, bpmn_id, event_definition, **kwargs):
        """
        Constructor.

        :param event_definition: the EventDefinition that we must wait for.
        """
        super().__init__(wf_spec, bpmn_id, **kwargs)
        self.event_definition = event_definition

    def catches(self, my_task, event):
        return my_task.task_spec.event_definition.catches(my_task, event)

    def catch(self, my_task, event):
        """
        Catch is called by the workflow when the task has matched an event
        definition, at which point we can update our task's state.
        """
        self.event_definition.catch(my_task, event)
        my_task.last_update_time = time.time()
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

        self.event_definition.update_task_data(my_task)
        self.event_definition.reset(my_task)
        return super()._run_hook(my_task)

    def _predict_hook(self, my_task):
        if not isinstance(self.event_definition, CycleTimerEventDefinition):
            super()._predict_hook(my_task)


class ThrowingEvent(TaskSpec):
    """Base Task Spec for Throwing Event nodes."""

    def __init__(self, wf_spec, bpmn_id, event_definition, **kwargs):
        """
        Constructor.

        :param event_definition: the EventDefinition to be thrown.
        """
        super().__init__(wf_spec, bpmn_id, **kwargs)
        self.event_definition = event_definition

    def _run_hook(self, my_task):
        super()._run_hook(my_task)
        self.event_definition.throw(my_task)
        return True
