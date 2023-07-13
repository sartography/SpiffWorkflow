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

from SpiffWorkflow.bpmn.serializer.helpers.spec import EventDefinitionConverter

from SpiffWorkflow.spiff.specs.event_definitions import (
    MessageEventDefinition,
    SignalEventDefinition,
    ErrorEventDefinition,
    EscalationEventDefinition,
)

class MessageEventDefinitionConverter(EventDefinitionConverter):

    def __init__(self, registry):
        super().__init__(MessageEventDefinition, registry)

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['correlation_properties'] = self.correlation_properties_to_dict(event_definition.correlation_properties)
        dct['expression'] = event_definition.expression
        dct['message_var'] = event_definition.message_var
        return dct

    def from_dict(self, dct):
        dct['correlation_properties'] = self.correlation_properties_from_dict(dct['correlation_properties'])
        event_definition = super().from_dict(dct)
        return event_definition


class ItemAwareEventDefinitionConverter(EventDefinitionConverter):

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['expression'] = event_definition.expression
        dct['variable'] = event_definition.variable
        return dct


class SignalEventDefinitionConverter(ItemAwareEventDefinitionConverter):
    def __init__(self, registry):
        super().__init__(SignalEventDefinition, registry)


class ErrorEventDefinitionConverter(ItemAwareEventDefinitionConverter):

    def __init__(self, registry):
        super().__init__(ErrorEventDefinition, registry)

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['code'] = event_definition.code
        return dct
    
class EscalationEventDefinitionConverter(ItemAwareEventDefinitionConverter):

    def __init__(self, registry):
        super().__init__(EscalationEventDefinition, registry)

    def to_dict(self, event_definition):
        dct = super().to_dict(event_definition)
        dct['code'] = event_definition.code
        return dct