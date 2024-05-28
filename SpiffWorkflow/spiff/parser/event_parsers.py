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

import warnings

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
from SpiffWorkflow.bpmn.parser.util import one, first
from SpiffWorkflow.bpmn.specs.event_definitions.message import CorrelationProperty
from SpiffWorkflow.spiff.parser.task_spec import SpiffTaskParser, SPIFFWORKFLOW_NSMAP


class SpiffEventDefinitionParser(SpiffTaskParser, EventDefinitionParser):

    def parse_message_extensions(self, node):
        expression = first(node.xpath('.//spiffworkflow:messagePayload', namespaces=SPIFFWORKFLOW_NSMAP))
        variable = first(node.xpath('.//spiffworkflow:messageVariable', namespaces=SPIFFWORKFLOW_NSMAP))
        if expression is not None:
            expression = expression.text
        if variable is not None:
            variable = variable.text
        return expression, variable

    def parse_process_correlations(self, node):
        correlations = []
        for prop in node.xpath('.//spiffworkflow:processVariableCorrelation', namespaces=SPIFFWORKFLOW_NSMAP):
            key = one(prop.xpath('./spiffworkflow:propertyId', namespaces=SPIFFWORKFLOW_NSMAP))
            expression = one(prop.xpath('./spiffworkflow:expression', namespaces=SPIFFWORKFLOW_NSMAP))
            correlations.append(CorrelationProperty(key.text, expression.text, []))
        return correlations

    def parse_message_event(self, message_event):
        """Parse a Spiff message event."""

        message_ref = message_event.get('messageRef')
        if message_ref:
            try:
                message = one(self.doc_xpath('.//bpmn:message[@id="%s"]' % message_ref))
            except Exception:
                self.raise_validation_exception('Expected a Message node', node=message_event)
            name = message.get('name')
            expression, variable = self.parse_message_extensions(message)
            if expression is not None or variable is not None:
                warnings.warn(
                    'spiffworkflow:messagePayload and spiffworkflow:messageVariable have been moved to the bpmn:messageDefinition element',
                    DeprecationWarning,
                    stacklevel=2,
                )
            else:
                expression, variable = self.parse_message_extensions(message_event)
            correlations = self.get_message_correlations(message_ref)
            process_correlations = self.parse_process_correlations(message_event)
            event_def = MessageEventDefinition(name, correlations, expression, variable, process_correlations)
        else:
            name = message_event.getparent().get('name')
            event_def = MessageEventDefinition(name)

        return event_def

    def parse_signal_event(self, signal_event):
        """Parse a Spiff signal event"""
        signal_ref = signal_event.get('signalRef')
        if signal_ref is not None:
            try:
                signal = one(self.doc_xpath(f'.//bpmn:signal[@id="{signal_ref}"]'))
            except Exception:
                self.raise_validation_exception('Expected a Signal node', node=signal_event)
            name = signal.get('name')
            extensions = self.parse_extensions(signal)
            expression = extensions.get('payloadExpression')
            variable = extensions.get('variableName')
        else:
            name = signal_event.getparent().get('name')
            expression, variable = None, None
        return SignalEventDefinition(name, expression=expression, variable=variable)

    def parse_error_event(self, error_event):
        """Parse a Spiff error event"""
        error_ref = error_event.get('errorRef')
        if error_ref is not None:
            try:
                error = one(self.doc_xpath(f'.//bpmn:error[@id="{error_ref}"]'))
            except Exception:
                self.raise_validation_exception('Expected an Error node', node=error_event)
            name = error.get('name')
            code = error.get('errorCode')
            extensions = self.parse_extensions(error)
            expression = extensions.get('payloadExpression')
            variable = extensions.get('variableName')
        else:
            name = error_event.getparent().get('name')
            code, expression, variable = None, None, None
        return ErrorEventDefinition(name, expression=expression, variable=variable, code=code)

    def parse_escalation_event(self, escalation_event):
        """Parse a Spiff error event"""
        escalation_ref = escalation_event.get('escalationRef')
        if escalation_ref is not None:
            try:
                escalation = one(self.doc_xpath(f'.//bpmn:escalation[@id="{escalation_ref}"]'))
            except Exception:
                self.raise_validation_exception('Expected an Escalation node', node=escalation_event)
            name = escalation.get('name')
            code = escalation.get('escalationCode')
            extensions = self.parse_extensions(escalation)
            expression = extensions.get('payloadExpression')
            variable = extensions.get('variableName')
        else:
            name = escalation_event.getparent().get('name')
            code, expression, variable = None, None, None
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
