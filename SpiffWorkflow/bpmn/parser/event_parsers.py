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

from lxml import etree

from .ValidationException import ValidationException
from .TaskParser import TaskParser
from .util import first, one

from SpiffWorkflow.bpmn.specs.event_definitions.simple import (
    NoneEventDefinition,
    CancelEventDefinition,
    TerminateEventDefinition
)
from SpiffWorkflow.bpmn.specs.event_definitions.timer import (
    TimeDateEventDefinition,
    DurationTimerEventDefinition,
    CycleTimerEventDefinition
)
from SpiffWorkflow.bpmn.specs.event_definitions.item_aware_event import (
    SignalEventDefinition,
    ErrorEventDefinition,
    EscalationEventDefinition
)
from SpiffWorkflow.bpmn.specs.event_definitions.message import (
    MessageEventDefinition,
    CorrelationProperty
)
from SpiffWorkflow.bpmn.specs.event_definitions.multiple import MultipleEventDefinition


CANCEL_EVENT_XPATH = './/bpmn:cancelEventDefinition'
ERROR_EVENT_XPATH = './/bpmn:errorEventDefinition'
ESCALATION_EVENT_XPATH = './/bpmn:escalationEventDefinition'
TERMINATION_EVENT_XPATH = './/bpmn:terminateEventDefinition'
MESSAGE_EVENT_XPATH = './/bpmn:messageEventDefinition'
SIGNAL_EVENT_XPATH = './/bpmn:signalEventDefinition'
TIMER_EVENT_XPATH = './/bpmn:timerEventDefinition'


class EventDefinitionParser(TaskParser):
    """This class provvides methods for parsing different event definitions."""

    def __init__(self, process_parser, spec_class, node, nsmap=None, lane=None):
        super().__init__(process_parser, spec_class, node, nsmap, lane)
        self.event_nodes = []

    def get_description(self):
        spec_description = super().get_description()
        if spec_description is not None:
            if len(self.event_nodes) == 0:
                event_description =  'Default'
            elif len(self.event_nodes) > 1:
                event_description = 'Multiple'
            elif len(self.event_nodes) == 1:
                event_description = self.process_parser.parser.spec_descriptions.get(self.event_nodes[0].tag)
            return f'{event_description} {spec_description}'

    def get_event_description(self, event):
        return self.process_parser.parser.spec_descriptions.get(event.tag)

    def parse_cancel_event(self, event):
        return CancelEventDefinition(description=self.get_event_description(event))

    def parse_error_event(self, error_event):
        """Parse the errorEventDefinition node and return an instance of ErrorEventDefinition."""
        error_ref = error_event.get('errorRef')
        if error_ref:
            error = one(self.doc_xpath('.//bpmn:error[@id="%s"]' % error_ref))
            error_code = error.get('errorCode')
            name = error.get('name')
        else:
            name, error_code = 'None Error Event', None
        return ErrorEventDefinition(name, error_code, description=self.get_event_description(error_event))

    def parse_escalation_event(self, escalation_event):
        """Parse the escalationEventDefinition node and return an instance of EscalationEventDefinition."""

        escalation_ref = escalation_event.get('escalationRef')
        if escalation_ref:
            escalation = one(self.doc_xpath('.//bpmn:escalation[@id="%s"]' % escalation_ref))
            escalation_code = escalation.get('escalationCode')
            name = escalation.get('name')
        else:
            name, escalation_code = 'None Escalation Event', None
        return EscalationEventDefinition(name, escalation_code, description=self.get_event_description(escalation_event))

    def parse_message_event(self, message_event):

        message_ref = message_event.get('messageRef')
        if message_ref is not None:
            message = one(self.doc_xpath('.//bpmn:message[@id="%s"]' % message_ref))
            name = message.get('name')
            description = self.get_event_description(message_event)
            correlations = self.get_message_correlations(message_ref)
        else:
            name = message_event.getparent().get('name')
            description = 'Message'
            correlations = {}
        return MessageEventDefinition(name, correlations, description=description)

    def parse_signal_event(self, signal_event):
        """Parse the signalEventDefinition node and return an instance of SignalEventDefinition."""

        signal_ref = signal_event.get('signalRef')
        if signal_ref:
            signal = one(self.doc_xpath('.//bpmn:signal[@id="%s"]' % signal_ref))
            name = signal.get('name')
        else:
            name = signal_event.getparent().get('name')
        return SignalEventDefinition(name, description=self.get_event_description(signal_event))

    def parse_terminate_event(self, event):
        """Parse the terminateEventDefinition node and return an instance of TerminateEventDefinition."""
        return TerminateEventDefinition(description=self.get_event_description(event))

    def parse_timer_event(self, event):
        """Parse the timerEventDefinition node and return an instance of TimerEventDefinition."""
        try:
            description = self.get_event_description(event)
            name = self.node.get('name', self.node.get('id'))
            time_date = first(self.xpath('.//bpmn:timeDate'))
            if time_date is not None:
                return TimeDateEventDefinition(name, time_date.text, description=description)
            time_duration = first(self.xpath('.//bpmn:timeDuration'))
            if time_duration is not None:
                return DurationTimerEventDefinition(name, time_duration.text, description=description)
            time_cycle = first(self.xpath('.//bpmn:timeCycle'))
            if time_cycle is not None:
                return CycleTimerEventDefinition(name, time_cycle.text, description=description)
            raise ValidationException("Unknown Time Specification", node=self.node, file_name=self.filename)
        except Exception as e:
            raise ValidationException("Time Specification Error. " + str(e), node=self.node, file_name=self.filename)

    def get_message_correlations(self, message_ref):

        correlations = []
        for correlation in self.doc_xpath(f".//bpmn:correlationPropertyRetrievalExpression[@messageRef='{message_ref}']"):
            key = correlation.getparent().get('id')
            children = correlation.getchildren()
            expression = children[0].text if len(children) > 0 else None
            used_by = [ e.getparent().get('name') for e in
                self.doc_xpath(f".//bpmn:correlationKey/bpmn:correlationPropertyRef[text()='{key}']") ]
            if key is not None and expression is not None:
                correlations.append(CorrelationProperty(key, expression, used_by))
        return correlations

    def _create_task(self, event_definition, cancel_activity=None, parallel=None):

        if isinstance(event_definition, MessageEventDefinition):
            for prop in event_definition.correlation_properties:
                for key in prop.correlation_keys:
                    if key not in self.spec.correlation_keys:
                        self.spec.correlation_keys[key] = []
                    if prop.name not in self.spec.correlation_keys[key]:
                        self.spec.correlation_keys[key].append(prop.name)

        kwargs = self.bpmn_attributes
        if cancel_activity is not None:
            kwargs['cancel_activity'] = cancel_activity
            interrupt = 'Interrupting' if cancel_activity else 'Non-Interrupting'
            kwargs['description'] = interrupt + ' ' + kwargs['description']
        if parallel is not None:
            kwargs['parallel'] = parallel
        return self.spec_class(self.spec, self.bpmn_id, event_definition=event_definition, **kwargs)

    def get_event_definition(self, xpaths):
        """Returns all event definitions it can find in given list of xpaths"""

        event_definitions = []
        for path in xpaths:
            for event in self.xpath(path):
                if event is not None:
                    self.event_nodes.append(event)
                if path == MESSAGE_EVENT_XPATH:
                    event_definitions.append(self.parse_message_event(event))
                elif path == SIGNAL_EVENT_XPATH:
                    event_definitions.append(self.parse_signal_event(event))
                elif path == TIMER_EVENT_XPATH:
                    event_definitions.append(self.parse_timer_event(event))
                elif path == CANCEL_EVENT_XPATH:
                    event_definitions.append(self.parse_cancel_event(event))
                elif path == ERROR_EVENT_XPATH:
                    event_definitions.append(self.parse_error_event(event))
                elif path == ESCALATION_EVENT_XPATH:
                    event_definitions.append(self.parse_escalation_event(event))
                elif path == TERMINATION_EVENT_XPATH:
                    event_definitions.append(self.parse_terminate_event(event))

        parallel = self.node.get('parallelMultiple') == 'true'

        if len(event_definitions) == 0:
            return NoneEventDefinition(description='Default')
        elif len(event_definitions) == 1:
            return event_definitions[0]
        else:
            return MultipleEventDefinition(event_definitions, parallel, description='Multiple')


class StartEventParser(EventDefinitionParser):
    """Parses a Start Event, and connects it to the internal spec.start task.
    Support Message, Signal, and Timer events."""

    def create_task(self):
        event_definition = self.get_event_definition([MESSAGE_EVENT_XPATH, SIGNAL_EVENT_XPATH, TIMER_EVENT_XPATH])
        task = self._create_task(event_definition)
        self.spec.start.connect(task)
        return task

    def handles_multiple_outgoing(self):
        return True


class EndEventParser(EventDefinitionParser):
    """Parses an End Event. Handles Termination, Escalation, Cancel, and Error End Events."""

    def create_task(self):
        event_definition = self.get_event_definition([MESSAGE_EVENT_XPATH, CANCEL_EVENT_XPATH, ERROR_EVENT_XPATH,
                                                      ESCALATION_EVENT_XPATH, TERMINATION_EVENT_XPATH])
        task = self._create_task(event_definition)
        task.connect(self.spec.end)
        return task


class IntermediateCatchEventParser(EventDefinitionParser):
    """Parses an Intermediate Catch Event. Currently supports Message, Signal, and Timer definitions."""

    def create_task(self):
        event_definition = self.get_event_definition([MESSAGE_EVENT_XPATH, SIGNAL_EVENT_XPATH, TIMER_EVENT_XPATH])
        return super()._create_task(event_definition)


class IntermediateThrowEventParser(EventDefinitionParser):
    """Parses an Intermediate Catch Event. Currently supports Message, Signal and Timer event definitions."""

    def create_task(self):
        event_definition = self.get_event_definition([ESCALATION_EVENT_XPATH, MESSAGE_EVENT_XPATH,
                                                      SIGNAL_EVENT_XPATH, TIMER_EVENT_XPATH])
        return self._create_task(event_definition)


class SendTaskParser(IntermediateThrowEventParser):

    def create_task(self):

        if self.node.get('messageRef') is not None:
            event_definition = self.parse_message_event(self.node)
        else:
            message_event = first(self.xpath(MESSAGE_EVENT_XPATH))
            if message_event is not None:
                event_definition = self.parse_message_event(message_event)
            else:
                event_definition = NoneEventDefinition()

        return self._create_task(event_definition)


class ReceiveTaskParser(SendTaskParser):
    """Identical to the SendTaskParser - check for a message event definition"""
    pass


class BoundaryEventParser(EventDefinitionParser):
    """
    Parse a Catching Boundary Event. This extends the
    IntermediateCatchEventParser in order to parse the event definition.
    """

    def create_task(self):
        cancel_activity = self.node.get('cancelActivity', default='true').lower() == 'true'
        event_definition = self.get_event_definition([CANCEL_EVENT_XPATH, ERROR_EVENT_XPATH, ESCALATION_EVENT_XPATH,
                                                      MESSAGE_EVENT_XPATH, SIGNAL_EVENT_XPATH, TIMER_EVENT_XPATH])
        if isinstance(event_definition, NoneEventDefinition):
            raise NotImplementedError('Unsupported Catch Event: %r', etree.tostring(self.node))
        return self._create_task(event_definition, cancel_activity)


class EventBasedGatewayParser(EventDefinitionParser):

    def create_task(self):
        return self._create_task(MultipleEventDefinition())

    def handles_multiple_outgoing(self):
        return True

    def connect_outgoing(self, outgoing_task, sequence_flow_node, is_default):
        self.task.event_definition.event_definitions.append(outgoing_task.event_definition)
        self.task.connect(outgoing_task)
