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

from SpiffWorkflow.bpmn.parser.event_parsers import EventDefinitionParser, ReceiveTaskParser
from SpiffWorkflow.bpmn.parser.event_parsers import (
    StartEventParser,
    EndEventParser,
    IntermediateCatchEventParser,
    IntermediateThrowEventParser,
    BoundaryEventParser,
    SendTaskParser,
)
from SpiffWorkflow.spiff.specs.event_definitions import (
    MessageEventDefinition,
    SignalEventDefinition,
    ErrorEventDefinition,
    EscalationEventDefinition,
)
from SpiffWorkflow.bpmn.parser.util import one
from SpiffWorkflow.spiff.parser.task_spec import SpiffTaskParser


class SpiffEventDefinitionParser(SpiffTaskParser, EventDefinitionParser):

    def parse_message_event(self, message_event):
        """Parse a Spiff message event."""

        message_ref = message_event.get('messageRef')
        if message_ref:
            message = one(self.doc_xpath('.//bpmn:message[@id="%s"]' % message_ref))
            name = message.get('name')
            extensions = self.parse_extensions(message)
            correlations = self.get_message_correlations(message_ref)
        else:
            name = message_event.getparent().get('name')
            extensions = {}
            correlations = []

        return MessageEventDefinition(name, correlations,
            expression=extensions.get('messagePayload'),
            message_var=extensions.get('messageVariable')
        )

    def parse_signal_event(self, signal_event):
        """Parse a Spiff signal event"""
        signal_ref = signal_event.get('signalRef')
        signal = one(self.doc_xpath(f'.//bpmn:signal[@id="{signal_ref}"]'))
        name = signal.get('name')
        extensions = self.parse_extensions(signal)
        expression = extensions.get('payloadExpression')
        variable = extensions.get('variableName')
        return SignalEventDefinition(name, expression=expression, variable=variable)

    def parse_error_event(self, error_event):
        """Parse a Spiff error event"""
        error_ref = error_event.get('errorRef')
        error = one(self.doc_xpath(f'.//bpmn:error[@id="{error_ref}"]'))
        name = error.get('name')
        code = error.get('errorCode')
        extensions = self.parse_extensions(error)
        expression = extensions.get('payloadExpression')
        variable = extensions.get('variableName')
        return ErrorEventDefinition(name, expression=expression, variable=variable, code=code)

    def parse_escalation_event(self, escalation_event):
        """Parse a Spiff error event"""
        escalation_ref = escalation_event.get('escalationRef')
        escalation = one(self.doc_xpath(f'.//bpmn:escalation[@id="{escalation_ref}"]'))
        name = escalation.get('name')
        code = escalation.get('escalationCode')
        extensions = self.parse_extensions(escalation)
        expression = extensions.get('payloadExpression')
        variable = extensions.get('variableName')
        return EscalationEventDefinition(name, expression=expression, variable=variable, code=code)


class SpiffStartEventParser(SpiffEventDefinitionParser, StartEventParser):
    def create_task(self):
        return StartEventParser.create_task(self)

class SpiffEndEventParser(SpiffEventDefinitionParser, EndEventParser):
    def create_task(self):
        return EndEventParser.create_task(self)

class SpiffIntermediateCatchEventParser(SpiffEventDefinitionParser, IntermediateCatchEventParser):
    def create_task(self):
        return IntermediateCatchEventParser.create_task(self)

class SpiffIntermediateThrowEventParser(SpiffEventDefinitionParser, IntermediateThrowEventParser):
    def create_task(self):
        return IntermediateThrowEventParser.create_task(self)

class SpiffBoundaryEventParser(SpiffEventDefinitionParser, BoundaryEventParser):
    def create_task(self):
        return BoundaryEventParser.create_task(self)

class SpiffSendTaskParser(SpiffEventDefinitionParser, SendTaskParser):
    def create_task(self):
        return SendTaskParser.create_task(self)

class SpiffReceiveTaskParser(SpiffEventDefinitionParser, ReceiveTaskParser):
    def create_task(self):
        return ReceiveTaskParser.create_task(self)
