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

from SpiffWorkflow.bpmn import BpmnEvent
from SpiffWorkflow.bpmn.specs.event_definitions import MessageEventDefinition

class MessageEventDefinition(MessageEventDefinition):
    """
    Message Events have both a name and a payload.
    """

    # It is not entirely clear how the payload is supposed to be handled, so I have
    # deviated from what the earlier code did as little as possible, but I believe
    # this should be revisited: for one thing, we're relying on some Camunda-specific
    # properties.

    def __init__(self, name, correlation_properties=None, expression=None, result_var=None, **kwargs):

        super(MessageEventDefinition, self).__init__(name, correlation_properties, **kwargs)
        self.expression = expression
        self.result_var = result_var

    def throw(self, my_task):
        result = my_task.workflow.script_engine.evaluate(my_task, self.expression)
        payload = {
            'payload': result,
            'result_var': self.result_var
        }
        event = BpmnEvent(self, payload=payload)
        my_task.workflow.top_workflow.catch(event)

    def update_internal_data(self, my_task, event):
        if event.payload.get('result_var') is None:
            event.payload['result_var'] = f'{my_task.task_spec.name}_Response'
        my_task.internal_data[self.name] = event.payload

    def update_task_data(self, my_task):
        event_data = my_task.internal_data.get(self.name)
        my_task.data[event_data['result_var']] = event_data['payload']

    def reset(self, my_task):
        my_task.internal_data.pop('result_var', None)
        super(MessageEventDefinition, self).reset(my_task)
