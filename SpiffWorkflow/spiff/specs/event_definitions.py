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

from SpiffWorkflow.bpmn.specs.event_definitions import MessageEventDefinition

class MessageEventDefinition(MessageEventDefinition):

    def __init__(self, name, correlation_properties=None, expression=None, message_var=None):

        super(MessageEventDefinition, self).__init__(name, correlation_properties)
        self.expression = expression
        self.message_var = message_var
        self.internal = False

    def throw(self, my_task):
        # We can't update our own payload, because if this task is reached again
        # we have to evaluate it again so we have to create a new event
        event = MessageEventDefinition(self.name, self.correlation_properties, self.expression, self.message_var)
        event.payload = my_task.workflow.script_engine.evaluate(my_task, self.expression)
        correlations = self.get_correlations(my_task, event.payload)
        my_task.workflow.correlations.update(correlations)
        self._throw(event, my_task.workflow, my_task.workflow.outer_workflow, correlations)

    def update_task_data(self, my_task):
        my_task.data[self.message_var] = my_task.internal_data[self.name]

    def reset(self, my_task):
        my_task.internal_data.pop(self.message_var, None)
        super(MessageEventDefinition, self).reset(my_task)
