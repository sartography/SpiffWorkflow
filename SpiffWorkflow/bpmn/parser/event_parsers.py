from lxml import etree

from SpiffWorkflow.bpmn.specs.events.event_definitions import CorrelationProperty

from .ValidationException import ValidationException
from .TaskParser import TaskParser
from .util import first, one
from ..specs.events import (TimerEventDefinition, MessageEventDefinition,
                            ErrorEventDefinition, EscalationEventDefinition,SignalEventDefinition,
                            CancelEventDefinition, CycleTimerEventDefinition,
                            TerminateEventDefinition, NoneEventDefinition)


CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'

class EventDefinitionParser(TaskParser):
    """This class provvides methods for parsing different event definitions."""

    def parse_cancel_event(self):
        return CancelEventDefinition()

    def parse_error_event(self, error_event):
        """Parse the errorEventDefinition node and return an instance of ErrorEventDefinition."""

        error_ref = error_event.get('errorRef')
        if error_ref:
            error = one(self.doc_xpath('.//bpmn:error[@id="%s"]' % error_ref))
            error_code = error.get('errorCode')
            name = error.get('name')
        else:
            name, error_code = 'None Error Event', None
        return ErrorEventDefinition(name, error_code)

    def parse_escalation_event(self, escalation_event):
        """Parse the escalationEventDefinition node and return an instance of EscalationEventDefinition."""

        escalation_ref = escalation_event.get('escalationRef')
        if escalation_ref:
            escalation = one(self.doc_xpath('.//bpmn:escalation[@id="%s"]' % escalation_ref))
            escalation_code = escalation.get('escalationCode')
            name = escalation.get('name')
        else:
            name, escalation_code = 'None Escalation Event', None
        return EscalationEventDefinition(name, escalation_code)

    def parse_message_event(self, message_event):

        message_ref = message_event.get('messageRef')
        if message_ref is not None:
            message = one(self.doc_xpath('.//bpmn:message[@id="%s"]' % message_ref))
            name = message.get('name')
            correlations = self.get_message_correlations(message_ref)
        else:
            name = message_event.getparent().get('name')
            correlations = {}
        return MessageEventDefinition(name, correlations)

    def parse_signal_event(self, signal_event):
        """Parse the signalEventDefinition node and return an instance of SignalEventDefinition."""

        signal_ref = signal_event.get('signalRef')
        if signal_ref:
            signal = one(self.doc_xpath('.//bpmn:signal[@id="%s"]' % signal_ref))
            name = signal.get('name')
        else:
            name = signal_event.getparent().get('name')
        return SignalEventDefinition(name)

    def parse_terminate_event(self):
        """Parse the terminateEventDefinition node and return an instance of TerminateEventDefinition."""
        return TerminateEventDefinition()

    def parse_timer_event(self, timer_event):
        """Parse the timerEventDefinition node and return an instance of TimerEventDefinition."""

        try:
            time_date = first(self.xpath('.//bpmn:timeDate'))
            if time_date is not None:
                return TimerEventDefinition(self.node.get('name'), time_date.text)

            time_duration = first(self.xpath('.//bpmn:timeDuration'))
            if time_duration is not None:
                return TimerEventDefinition(self.node.get('name'), time_duration.text)

            time_cycle = first(self.xpath('.//bpmn:timeCycle'))
            if time_cycle is not None:
                return CycleTimerEventDefinition(self.node.get('name'), time_cycle.text)
        except:
            raise ValidationException("Unknown Time Specification", node=self.node, filename=self.filename)

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

    def _create_task(self, event_definition, cancel_activity=None):

        if isinstance(event_definition, MessageEventDefinition):
            for prop in event_definition.correlation_properties:
                for key in prop.correlation_keys:
                    if key not in self.spec.correlation_keys:
                        self.spec.correlation_keys[key] = []
                    if prop.name not in self.spec.correlation_keys[key]:
                        self.spec.correlation_keys[key].append(prop.name)

        kwargs = {
            'lane': self.lane,
            'description': self.node.get('name', None),
            'position': self.position,
        }
        if cancel_activity is not None:
            kwargs['cancel_activity'] = cancel_activity
        return self.spec_class(self.spec, self.get_task_spec_name(), event_definition, **kwargs)


class StartEventParser(EventDefinitionParser):
    """Parses a Start Event, and connects it to the internal spec.start task.  Support Message, Signal, and Timer events."""

    def create_task(self):

        messageEvent = first(self.xpath('.//bpmn:messageEventDefinition'))
        signalEvent = first(self.xpath('.//bpmn:signalEventDefinition'))
        timerEvent = first(self.xpath('.//bpmn:timerEventDefinition'))

        if messageEvent is not None:
            event_definition = self.parse_message_event(messageEvent)
        elif signalEvent is not None:
            event_definition = self.parse_signal_event(signalEvent)
        elif timerEvent is not None:
            event_definition = self.parse_timer_event(timerEvent)
        else:
            event_definition = NoneEventDefinition()

        task = self._create_task(event_definition)
        self.spec.start.connect(task)
        if isinstance(event_definition, CycleTimerEventDefinition):
            # We are misusing cycle timers, so this is a hack whereboy we will
            # revisit ourself if we fire.
            task.connect(task)
        return task

    def handles_multiple_outgoing(self):
        return True


class EndEventParser(EventDefinitionParser):
    """Parses an End Event. Handles Termination, Escalation, Cancel, and Error End Events."""

    def create_task(self):

        cancelEvent = first(self.xpath('.//bpmn:cancelEventDefinition'))
        errorEvent = first(self.xpath('.//bpmn:errorEventDefinition'))
        escalationEvent = first(self.xpath('.//bpmn:escalationEventDefinition'))
        terminateEvent = first(self.xpath('.//bpmn:terminateEventDefinition'))
        messageEvent = first(self.xpath('.//bpmn:messageEventDefinition'))

        if messageEvent is not None:
            event_definition = self.parse_message_event(messageEvent)
        elif cancelEvent is not None:
            event_definition = self.parse_cancel_event()
        elif errorEvent is not None:
            event_definition = self.parse_error_event(errorEvent)
        elif escalationEvent is not None:
            event_definition = self.parse_escalation_event(escalationEvent)
        elif terminateEvent is not None:
            event_definition = self.parse_terminate_event()
        else:
            event_definition = NoneEventDefinition()

        task = self._create_task(event_definition)
        task.connect_outgoing(self.spec.end, '%s.ToEndJoin' % self.node.get('id'), None, None)
        return task


class IntermediateCatchEventParser(EventDefinitionParser):
    """Parses an Intermediate Catch Event. Currently supports Message, Signal, and Timer definitions."""

    def create_task(self):

        messageEvent = first(self.xpath('.//bpmn:messageEventDefinition'))
        signalEvent = first(self.xpath('.//bpmn:signalEventDefinition'))
        timerEvent = first(self.xpath('.//bpmn:timerEventDefinition'))

        if messageEvent is not None:
            event_definition = self.parse_message_event(messageEvent)
        elif signalEvent is not None:
            event_definition = self.parse_signal_event(signalEvent)
        elif timerEvent is not None:
            event_definition = self.parse_timer_event(timerEvent)
        else:
            event_definition = NoneEventDefinition()

        return super()._create_task(event_definition)


class IntermediateThrowEventParser(EventDefinitionParser):
    """Parses an Intermediate Catch Event. Currently supports Message, Signal and Timer event definitions."""

    def create_task(self):

        escalationEvent = first(self.xpath('.//bpmn:escalationEventDefinition'))
        messageEvent = first(self.xpath('.//bpmn:messageEventDefinition'))
        signalEvent = first(self.xpath('.//bpmn:signalEventDefinition'))
        timerEvent = first(self.xpath('.//bpmn:timerEventDefinition'))

        if escalationEvent is not None:
            event_definition = self.parse_escalation_event(escalationEvent)
        elif messageEvent is not None:
            event_definition = self.parse_message_event(messageEvent)
        elif signalEvent is not None:
            event_definition = self.parse_signal_event(signalEvent)
        elif timerEvent is not None:
            event_definition = self.parse_timer_event(timerEvent)
        else:
            event_definition = NoneEventDefinition()

        return self._create_task(event_definition)


class SendTaskParser(IntermediateThrowEventParser):

    def create_task(self):

        if self.node.get('messageRef') is not None:
            event_definition = self.parse_message_event(self.node)
        else:
            message_event = first(self.xpath('.//bpmn:messageEventDefinition'))
            if message_event is not None:
                event_definition = self.parse_message_event(message_event)
            else:
                event_definition = NoneEventDefinition()

        return self._create_task(event_definition)


class ReceiveTaskParser(IntermediateCatchEventParser):

    def create_task(self):

        if self.node.get('messageRef') is not None:
            event_definition = self.parse_message_event(self.node)
        else:
            message_event = first(self.xpath('.//bpmn:messageEventDefinition'))
            if message_event is not None:
                event_definition = self.parse_message_event(message_event)
            else:
                event_definition = NoneEventDefinition()

        return self._create_task(event_definition)


class BoundaryEventParser(EventDefinitionParser):
    """
    Parse a Catching Boundary Event. This extends the
    IntermediateCatchEventParser in order to parse the event definition.
    """

    def create_task(self):

        cancel_activity = self.node.get('cancelActivity', default='true').lower() == 'true'

        cancelEvent = first(self.xpath('.//bpmn:cancelEventDefinition'))
        errorEvent = first(self.xpath('.//bpmn:errorEventDefinition'))
        escalationEvent = first(self.xpath('.//bpmn:escalationEventDefinition'))
        messageEvent = first(self.xpath('.//bpmn:messageEventDefinition'))
        signalEvent = first(self.xpath('.//bpmn:signalEventDefinition'))
        timerEvent = first(self.xpath('.//bpmn:timerEventDefinition'))

        if cancelEvent is not None:
            event_definition = self.parse_cancel_event()
        elif errorEvent is not None:
            event_definition = self.parse_error_event(errorEvent)
        elif escalationEvent is not None:
            event_definition = self.parse_escalation_event(escalationEvent)
        elif messageEvent is not None:
            event_definition = self.parse_message_event(messageEvent)
        elif signalEvent is not None:
            event_definition = self.parse_signal_event(signalEvent)
        elif timerEvent is not None:
            event_definition = self.parse_timer_event(timerEvent)
        else:
            raise NotImplementedError('Unsupported Catch Event: %r', etree.tostring(self.node))

        return self._create_task(event_definition, cancel_activity)
