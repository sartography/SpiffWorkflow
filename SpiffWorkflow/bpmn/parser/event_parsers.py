from lxml import etree

from .ValidationException import ValidationException
from .TaskParser import TaskParser
from .util import first, one
from ..specs.events import (TimerEventDefinition, MessageEventDefinition,
                            ErrorEventDefinition, EscalationEventDefinition,SignalEventDefinition,
                            CancelEventDefinition, CycleTimerEventDefinition,
                            TerminateEventDefinition, NoneEventDefinition,
                            StartEvent, EndEvent, BoundaryEvent, IntermediateCatchEvent, IntermediateThrowEvent)


CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'

class EventDefinitionParser(TaskParser):
    """This class provvides methods for parsing different event definitions."""

    def parse_cancel_event(self, cancelEvent):
        return CancelEventDefinition()

    def parse_error_event(self, errorEvent):
        """Parse the errorEventDefinition node and return an instance of ErrorEventDefinition."""

        errorRef = errorEvent.get('errorRef')
        if errorRef:
            error = one(self.process_parser.doc_xpath('.//bpmn:error[@id="%s"]' % errorRef))
            error_code = error.get('errorCode')
            name = error.get('name')
        else:
            name, error_code = 'None Error Event', None
        return ErrorEventDefinition(name, error_code)

    def parse_escalation_event(self, escalationEvent):
        """Parse the escalationEventDefinition node and return an instance of EscalationEventDefinition."""

        escalationRef = escalationEvent.get('escalationRef')
        if escalationRef:
            escalation = one(self.process_parser.doc_xpath('.//bpmn:escalation[@id="%s"]' % escalationRef))
            escalation_code = escalation.get('escalationCode')
            name = escalation.get('name')
        else:
            name, escalation_code = 'None Escalation Event', None
        return EscalationEventDefinition(name, escalation_code)

    def parse_message_event(self, messageEvent):
        """Parse the messageEventDefinition node and return an instance of MessageEventDefinition."""     

        messageRef = messageEvent.get('messageRef')
        if messageRef:
            message = one(self.process_parser.doc_xpath('.//bpmn:message[@id="%s"]' % messageRef))
            name = message.get('name')
        else:
            name = messageEvent.getparent().get('name')
        payload = messageEvent.attrib.get('{' + CAMUNDA_MODEL_NS + '}expression')
        resultVar = messageEvent.attrib.get('{' + CAMUNDA_MODEL_NS + '}resultVariable')
        return MessageEventDefinition(name, payload, resultVar)

    def parse_signal_event(self, signalEvent):
        """Parse the signalEventDefinition node and return an instance of SignalEventDefinition."""
        
        signalRef = signalEvent.get('signalRef')
        if signalRef:
            signal = one(self.process_parser.doc_xpath('.//bpmn:signal[@id="%s"]' % signalRef))
            name = signal.get('name')
        else:
            name = signalEvent.getparent().get('name')
        return SignalEventDefinition(name)

    def parse_terminate_event(self, terminateEvent):
        """Parse the terminateEventDefinition node and return an instance of TerminateEventDefinition."""
        return TerminateEventDefinition()

    def parse_timer_event(self, timerEvent):
        """Parse the timerEventDefinition node and return an instance of TimerEventDefinition."""

        try:
            timeDate = first(self.xpath('.//bpmn:timeDate'))
            if timeDate is not None:
                return TimerEventDefinition(self.node.get('name'), timeDate.text)

            timeDuration = first(self.xpath('.//bpmn:timeDuration'))
            if timeDuration is not None:
                return TimerEventDefinition(self.node.get('name'), timeDuration.text)

            timeCycle = first(self.xpath('.//bpmn:timeCycle'))
            if timeCycle is not None:
                return CycleTimerEventDefinition(self.node.get('name'), timeCycle.text)
        except:
            raise ValidationException("Unknown Time Specification", node=self.node, filename=self.process_parser.filename)


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

        kwargs = {
            'lane': self.get_lane(),
            'description': self.node.get('name', None),
            'position': self.process_parser.get_coord(self.get_id()),
        }
        task = StartEvent(self.spec, self.get_task_spec_name(), event_definition, **kwargs)
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

        if cancelEvent is not None:
            event_definition = self.parse_cancel_event(cancelEvent)
        elif errorEvent is not None:
            event_definition = self.parse_error_event(errorEvent)
        elif escalationEvent is not None:
            event_definition = self.parse_escalation_event(escalationEvent)
        elif terminateEvent is not None:
            event_definition = self.parse_terminate_event(terminateEvent)
        else:
            event_definition = NoneEventDefinition()

        kwargs = {
            'lane': self.get_lane(),
            'description': self.node.get('name', None),
            'position': self.process_parser.get_coord(self.get_id()),
        }
        task = EndEvent(self.spec, self.get_task_spec_name(), event_definition, **kwargs)
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
            raise NotImplementedError('Unsupported Intermediate Catch Event: %r', etree.tostring(self.node))

        kwargs = {
            'lane': self.get_lane(),
            'description': self.node.get('name', None),
            'position': self.process_parser.get_coord(self.get_id()),
        }
        return IntermediateCatchEvent(self.spec, self.get_task_spec_name(), event_definition, **kwargs)

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
            raise NotImplementedError('Unsupported Throw Event: %r', etree.tostring(self.node))

        kwargs = {
            'lane': self.get_lane(),
            'description': self.node.get('name', None),
            'position': self.process_parser.get_coord(self.get_id()),
        }
        return IntermediateThrowEvent(self.spec, self.get_task_spec_name(), event_definition, **kwargs)

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
            event_definition = self.parse_cancel_event(cancelEvent)
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

        kwargs = {
            'lane': self.get_lane(),
            'description': self.node.get('name', None),
            'position': self.process_parser.get_coord(self.get_id()),
        }
        return BoundaryEvent(self.spec, self.get_task_spec_name(), event_definition, cancel_activity, **kwargs)
