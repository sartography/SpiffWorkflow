# Copyright (C) 2023 Sartography
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

from SpiffWorkflow.bpmn.specs.event_definitions import (
    MessageEventDefinition,
    ErrorEventDefinition,
    EscalationEventDefinition,
    SignalEventDefinition,
)
from SpiffWorkflow.bpmn.specs.event_definitions.item_aware_event import ItemAwareEventDefinition
from SpiffWorkflow.bpmn import BpmnEvent

class MessageEventDefinition(MessageEventDefinition):

    def __init__(self, name, correlation_properties=None, expression=None, message_var=None, process_correlations=None, **kwargs):
        super(MessageEventDefinition, self).__init__(name, correlation_properties, **kwargs)
        self.expression = expression
        self.message_var = message_var
        self.process_correlations = process_correlations or []

    def throw(self, my_task):
        payload = my_task.workflow.script_engine.evaluate(my_task, self.expression)
        correlations = self.get_correlations(my_task, payload)
        event = BpmnEvent(self, payload=payload, correlations=correlations)
        my_task.workflow.correlations.update(correlations)
        my_task.workflow.top_workflow.catch(event)

    def update_task(self, my_task):
        correlations = self.calculate_correlations(
            my_task.workflow.script_engine,
            self.process_correlations,
            my_task.data
        )
        my_task.workflow.correlations.update(correlations)

    def update_task_data(self, my_task):
        if self.message_var is not None:
            my_task.data[self.message_var] = my_task.internal_data.pop(self.name)

    def reset(self, my_task):
        my_task.internal_data.pop(self.message_var, None)
        super(MessageEventDefinition, self).reset(my_task)


class SpiffItemAwareEventDefinition(ItemAwareEventDefinition):

    def __init__(self, name, expression=None, variable=None, **kwargs):
        super().__init__(name, **kwargs)
        self.expression = expression
        self.variable = variable

    def throw(self, my_task):
        if self.expression is not None:
            payload = my_task.workflow.script_engine.evaluate(my_task, self.expression)
        else:
            payload = None
        event = BpmnEvent(self, payload=payload)
        my_task.workflow.top_workflow.catch(event)

    def update_task_data(self, my_task):
        if self.variable is not None:
            my_task.data[self.variable] = my_task.internal_data.pop(self.name, None)

    def reset(self, my_task):
        my_task.internal_data.pop(self.name, None)
        super().reset(my_task)


class SignalEventDefinition(SpiffItemAwareEventDefinition, SignalEventDefinition):
    pass

class ErrorEventDefinition(SpiffItemAwareEventDefinition, ErrorEventDefinition):
    pass

class EscalationEventDefinition(SpiffItemAwareEventDefinition, EscalationEventDefinition):
    pass
