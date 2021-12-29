# -*- coding: utf-8 -*-
from __future__ import division
# Copyright (C) 2012 Matthew Hampton
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

from .ValidationException import ValidationException
from .TaskParser import TaskParser
from ..workflow import BpmnWorkflow
from .util import first, one
from ..specs.event_definitions import (TimerEventDefinition,
                                       MessageEventDefinition,
                                       EscalationEventDefinition,
                                       SignalEventDefinition,
                                       CancelEventDefinition, CycleTimerEventDefinition)
from lxml import etree
import copy
from ...exceptions import WorkflowException
from ...bpmn.specs.IntermediateCatchEvent import IntermediateCatchEvent
CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'

class StartEventParser(TaskParser):

    """
    Parses a Start Event, and connects it to the internal spec.start task.
    """

    def create_task(self):

        isMessageCatchingEvent = self.xpath('.//bpmn:messageEventDefinition')
        isSignalCatchingEvent = self.xpath('.//bpmn:signalEventDefinition')
        isCancelCatchingEvent = self.xpath('.//bpmn:cancelEventDefinition')
        isTimerCatchingEvent = self.xpath('.//bpmn:timerEventDefinition')

        if (len(isMessageCatchingEvent) > 0)\
                or (len(isSignalCatchingEvent) > 0) \
                or (len(isCancelCatchingEvent) > 0) \
                or (len(isTimerCatchingEvent) > 0)\
                :
            # we need to fix this up to wait on an event

            self.__class__ = type(self.get_id() + '_class', (
            self.__class__, IntermediateCatchEventParser), {})
            self.spec_class = IntermediateCatchEvent
            t = IntermediateCatchEventParser.create_task(self)
            self.spec.start.connect(t)
            return t
        t = super(StartEventParser, self).create_task()
        self.spec.start.connect(t)
        return t

    def handles_multiple_outgoing(self):
        return True


class EndEventParser(TaskParser):
    """
    Parses and End Event. This also checks whether it should be a terminating
    or escalation end event.
    """

    def create_task(self):

        terminate_event_definition = first(self.xpath('.//bpmn:terminateEventDefinition'))
        escalation_code = None
        escalation_event_definition = first(self.xpath('.//bpmn:escalationEventDefinition'))
        if escalation_event_definition is not None:
            escalation_ref = escalation_event_definition.get('escalationRef')
            if escalation_ref:
                escalation = one(self.process_parser.doc_xpath(
                    './/bpmn:escalation[@id="%s"]' % escalation_ref))
                escalation_code = escalation.get('escalationCode')
        cancel_event_definition = first(self.xpath('.//bpmn:cancelEventDefinition'))

        task = self.spec_class(self.spec, self.get_task_spec_name(),
                               is_terminate_event=terminate_event_definition is not None,
                               is_escalation_event=escalation_event_definition is not None,
                               escalation_code=escalation_code,
                               is_cancel_event=cancel_event_definition is not None,
                               description=self.node.get('name', None))
        task.connect_outgoing(self.spec.end, '%s.ToEndJoin' %
                              self.node.get('id'), None, None)
        return task


class UserTaskParser(TaskParser):

    """
    Base class for parsing User Tasks
    """
    pass


class ManualTaskParser(UserTaskParser):

    """
    Base class for parsing Manual Tasks. Currently assumes that Manual Tasks
    should be treated the same way as User Tasks.
    """
    pass


class NoneTaskParser(UserTaskParser):

    """
    Base class for parsing unspecified Tasks. Currently assumes that such Tasks
    should be treated the same way as User Tasks.
    """
    pass


class ExclusiveGatewayParser(TaskParser):
    """
    Parses an Exclusive Gateway, setting up the outgoing conditions
    appropriately.
    """

    def connect_outgoing(self, outgoing_task, outgoing_task_node,
                         sequence_flow_node, is_default):
        if is_default:
            super(ExclusiveGatewayParser, self).connect_outgoing(
                outgoing_task, outgoing_task_node, sequence_flow_node,
                is_default)
        else:
            cond = self.parser._parse_condition(
                outgoing_task, outgoing_task_node, sequence_flow_node,
                task_parser=self)
            if cond is None:
                raise ValidationException(
                    'Non-default exclusive outgoing sequence flow '
                    ' without condition',
                    sequence_flow_node,
                    self.process_parser.filename)
            self.task.connect_outgoing_if(
                cond, outgoing_task,
                sequence_flow_node.get('id'),
                sequence_flow_node.get('name', None),
                self.parser._parse_documentation(
                    sequence_flow_node, task_parser=self))

    def handles_multiple_outgoing(self):
        return True


class ParallelGatewayParser(TaskParser):

    """
    Parses a Parallel Gateway.
    """

    def handles_multiple_outgoing(self):
        return True


class InclusiveGatewayParser(TaskParser):

    """
    Parses an Inclusive Gateway.
    """

    def handles_multiple_outgoing(self):
        """
        At the moment I haven't implemented support for diverging inclusive
        gateways
        """
        return False


class SubWorkflowParser(TaskParser):

    """
    Base class for parsing unspecified Tasks. Currently assumes that such Tasks
    should be treated the same way as User Tasks.
    """
    def create_task(self):
        wf_spec = self.get_subprocess_parser()
        return self.spec_class(
            self.spec, self.get_task_spec_name(), bpmn_wf_spec=wf_spec,
            bpmn_wf_class=self.parser.WORKFLOW_CLASS,
            position=self.process_parser.get_coord(self.get_id()),
            description=self.node.get('name', None))


    def get_subprocess_parser(self):
        thisTask = self.process_xpath('.//*[@id="%s"]'% self.get_id())[0]
        workflowStartEvent = self.process_xpath('.//*[@id="%s"]/bpmn:startEvent' % self.get_id())
        workflowEndEvent =  self.process_xpath('.//*[@id="%s"]/bpmn:endEvent' % self.get_id())
        if len(workflowStartEvent) != 1:
            raise ValidationException(
                'Multiple Start points are not allowed in SubWorkflow Task',
                node=self.node,
                filename=self.process_parser.filename)
        if len(workflowEndEvent) == 0:
            raise ValidationException(
                'A SubWorkflow Must contain an End event',
                node=self.node,
                filename=self.process_parser.filename)
        thisTaskCopy = copy.deepcopy(thisTask)
        definitions = {'bpmn':"http://www.omg.org/spec/BPMN/20100524/MODEL",
                       'bpmndi':"http://www.omg.org/spec/BPMN/20100524/DI",
                       'dc':"http://www.omg.org/spec/DD/20100524/DC",
                       'camunda':"http://camunda.org/schema/1.0/bpmn",
                       'di':"http://www.omg.org/spec/DD/20100524/DI"}
        # Create wrapper xml for the subworkflow
        for ns in definitions.keys():
            etree.register_namespace(ns,definitions[ns])
        #root = etree.Element('bpmn:definitions')
        root = etree.Element('{'+definitions['bpmn']+'}definitions')

        # Change the subProcess into a new bpmn:process & change the ID
        thisTaskCopy.tag='{'+definitions['bpmn']+'}process'
        thisTaskCopy.set('id',thisTaskCopy.get('id')+"_process")
        thisTaskCopy.set('isExecutable','true')
        #inject the subWorkflow process into the header
        root.append(thisTaskCopy)
        # we have to put xml into our taskspec because
        # the actual workflow spec will not serialize to
        # json, but the XML is just a string

        xml = etree.tostring(root).decode('ascii')
        workflow_name = thisTaskCopy.get('id')

        self.parser.add_bpmn_xml(etree.fromstring(xml))
        wf_spec = self.parser.get_spec(workflow_name)
        wf_spec.file = self.process_parser.filename
        return wf_spec


class CallActivityParser(SubWorkflowParser):
    """
    Parses a CallActivity node. This also supports the not-quite-correct BPMN
    that Signavio produces (which does not have a calledElement attribute).
    """

    def create_task(self):
        wf_spec = self.get_subprocess_parser().get_spec()
        return self.spec_class(
            self.spec, self.get_task_spec_name(), bpmn_wf_spec=wf_spec,
            bpmn_wf_class=self.parser.WORKFLOW_CLASS,
            position=self.process_parser.get_coord(self.get_id()),
            description=self.node.get('name', None))

    def get_subprocess_parser(self):
        calledElement = self.node.get('calledElement', None)
        if not calledElement:
            raise ValidationException(
                'No "calledElement" attribute for Call Activity.',
                node=self.node,
                filename=self.process_parser.filename)
        process = self.parser.get_process_parser(calledElement)
        if process is None:
            raise ValidationException(
                f"The process '{calledElement}' was not found. Did you mean one of the following: "
                f"{', '.join(self.parser.get_process_ids())}?",
                node=self.node,
                filename=self.process_parser.filename)
        return process


class TransactionSubprocessParser(SubWorkflowParser):
    """Parses a transaction node"""
    
    def create_task(self):
        wf_spec = self.get_subprocess_parser()
        return self.spec_class(
            self.spec, self.get_task_spec_name(), bpmn_wf_spec=wf_spec,
            bpmn_wf_class=self.parser.WORKFLOW_CLASS,
            position=self.process_parser.get_coord(self.get_id()),
            description=self.node.get('name', None))


class ScriptTaskParser(TaskParser):
    """
    Parses a script task
    """

    def create_task(self):
        script = self.get_script()
        return self.spec_class(self.spec, self.get_task_spec_name(), script,
                               lane=self.get_lane(),
                               position=self.process_parser.get_coord(
                                   self.get_id()),
                               description=self.node.get('name', None))

    def get_script(self):
        """
        Gets the script content from the node. A subclass can override this
        method, if the script needs to be pre-parsed. The result of this call
        will be passed to the Script Engine for execution.
        """
        try:
            return one(self.xpath('.//bpmn:script')).text
        except AssertionError as ae:
            raise ValidationException(
                f"Invalid Script Task.  No Script Provided. ",
                node=self.node, filename=self.process_parser.filename)

class IntermediateCatchEventParser(TaskParser):
    """
    Parses an Intermediate Catch Event. This currently only supports Message
    and Timer event definitions.
    """

    def create_task(self):
        event_definition = self.get_event_definition()
        return self.spec_class(
            self.spec, self.get_task_spec_name(), event_definition,
            lane = self.get_lane(),
            description=self.node.get('name', None))

    def get_event_definition(self):
        """
        Parse the event definition node, and return an instance of Event
        """
        messageEventDefinition = first(
            self.xpath('.//bpmn:messageEventDefinition'))
        if messageEventDefinition is not None:
            return self.get_message_event_definition(messageEventDefinition)

        signalEventDefinition = first(
            self.xpath('.//bpmn:signalEventDefinition'))
        if signalEventDefinition is not None:
            return self.get_signal_event_definition(signalEventDefinition)

        cancelEventDefinition = first(
            self.xpath('.//bpmn:cancelEventDefinition'))
        if cancelEventDefinition is not None:
            return self.get_cancel_event_definition(cancelEventDefinition)

        timerEventDefinition = first(
            self.xpath('.//bpmn:timerEventDefinition'))
        if timerEventDefinition is not None:
            return self.get_timer_event_definition(timerEventDefinition)

        escalationEventDefinition = first(
            self.xpath('.//bpmn:escalationEventDefinition'))
        if escalationEventDefinition is not None:
            return self.get_escalation_event_definition(
                escalationEventDefinition)

        raise NotImplementedError(
            'Unsupported Intermediate Catch Event: %r', etree.tostring(self.node))

    def get_escalation_event_definition(self, escalationEventDefinition):
        """
        Parse the escalationEventDefinition node and return an instance of
        EscalationEventDefinition
        """
        escalationRef = escalationEventDefinition.get('escalationRef')
        if escalationRef:
            escalation = one(self.process_parser.doc_xpath('.//bpmn:escalation[@id="%s"]' % escalationRef))
            escalation_code = escalation.get('escalationCode')
        else:
            escalation_code = None
        return EscalationEventDefinition(escalation_code)

    def get_message_event_definition(self, messageEventDefinition):
        """
        Parse the messageEventDefinition node and return an instance of
        MessageEventDefinition
        """
        # we have two different modelers that handle messages
        # in different ways.
        # first the Signavio :
        messageRef = first(self.xpath('.//bpmn:messageRef'))
        if messageRef is not None:
            message = messageRef.get('name')
        elif messageEventDefinition is not None:
            message = messageEventDefinition.get('messageRef')
            if message is None:
                message = self.node.get('name')
        return MessageEventDefinition(message,name=self.process_parser.message_lookup.get(message,''))

    def get_signal_event_definition(self, signalEventDefinition):
        """
        Parse the messageEventDefinition node and return an instance of
        MessageEventDefinition
        """
        # we have two different modelers that handle messages
        # in different ways.
        # first the Signavio :
        signalRef = first(self.xpath('.//bpmn:signalRef'))
        if signalRef is not None:
            message = signalRef.get('name')
        elif signalEventDefinition is not None:
            message = signalEventDefinition.get('signalRef')
            if message is None:
                message = self.node.get('name')
        return SignalEventDefinition(message,name=self.process_parser.message_lookup.get(message,''))

    def get_cancel_event_definition(self, cancelEventDefinition):
        """
        Parse the messageEventDefinition node and return an instance of
        MessageEventDefinition
        """
        # we have two different modelers that handle messages
        # in different ways.
        # first the Signavio :
        cancelRef = first(self.xpath('.//bpmn:cancelRef'))
        if cancelRef is not None:
            message = cancelRef.get('name')
        elif cancelEventDefinition is not None:
            message = cancelEventDefinition.get('cancelRef')
            if message is None:
                message = self.node.get('name')
        return CancelEventDefinition(message,name=self.process_parser.message_lookup.get(message,''))

    def get_timer_event_definition(self, timerEventDefinition):
        """
        Parse the timerEventDefinition node and return an instance of
        TimerEventDefinition

        This currently only supports the timeDate node for specifying an expiry
        time for the timer.

        =============================
        WIP: add other definitions such as timeDuration and timeCycle
        for both timeDuration and timeCycle - from when?? certainly not from the time
        we parse the document, so how do we define total time inside a process or subprocess?


        Furthermore . . .

        do we add a start time for any process that we are working on, i.e. do I need to add a begin time for a
        subprocess to use a timer boundary event? or do we start the timer on entry?

        What about a process that has a duration of 5 days and no one actually touches the workflow for 7 days? How
        does this get triggered when no one is using the workflow on a day-to-day basis - do we need a cron job to go
        discover waiting tasks and fire them if no one is doing anything?

        """
        timeDate = first(self.xpath('.//bpmn:timeDate'))

        if timeDate is not None:
            return TimerEventDefinition(
                      self.node.get('name'),
                      timeDate.text)
#                      self.parser.parse_condition(
#                              timeDate.text, None, None, None, None, self))
        # in the case that it is a duration
        timeDuration = first(self.xpath('.//bpmn:timeDuration'))
        if timeDuration is not None:
            return TimerEventDefinition(
                      self.node.get('name'),
                      timeDuration.text)
#                self.parser.parse_condition(
#                    timeDuration.text, None, None, None, None, self))

        # in the case that it is a cycle - for now, it is an error
        timeCycle = first(self.xpath('.//bpmn:timeCycle'))
        if timeCycle is not None:
            return CycleTimerEventDefinition(
            self.node.get('name'),timeCycle.text)
#            self.parser.parse_condition(
#                   timeCycle.text, None, None, None, None, self))
        raise ValidationException("Unknown Time Specification",
                                  node=self.node,
                                  filename=self.process_parser.filename)

class IntermediateThrowEventParser(TaskParser):
    """
    Parses an Intermediate Catch Event. This currently onlt supports Message
    and Timer event definitions.
    """

    def create_task(self):
        event_definition = self.get_event_definition()
        return self.spec_class(
            self.spec, self.get_task_spec_name(), event_definition,
            lane=self.get_lane(),
            description=self.node.get('name', None))

    def get_event_definition(self):
        """
        Parse the event definition node, and return an instance of Event
        """
        messageEventDefinition = first(
            self.xpath('.//bpmn:messageEventDefinition'))
        if messageEventDefinition is not None:
            return self.get_message_event_definition(messageEventDefinition)

        signalEventDefinition = first(
            self.xpath('.//bpmn:signalEventDefinition'))
        if signalEventDefinition is not None:
            return self.get_signal_event_definition(signalEventDefinition)

        cancelEventDefinition = first(
            self.xpath('.//bpmn:cancelEventDefinition'))
        if cancelEventDefinition is not None:
            return self.get_cancel_event_definition(cancelEventDefinition)

            raise NotImplementedError(
            'Unsupported Intermediate Catch Event: %r', etree.tostring(self.node))

    def get_message_event_definition(self, messageEventDefinition):
        """
        Parse the messageEventDefinition node and return an instance of
        MessageEventDefinition
        """
        #messageRef = first(self.xpath('.//bpmn:messageEventDefinition'))
        name = self.node.get('name')
        message = messageEventDefinition.get(
            'messageRef') if messageEventDefinition is not None else name

        payload = messageEventDefinition.attrib.get('{' + CAMUNDA_MODEL_NS + '}expression')
        resultVar = messageEventDefinition.attrib.get('{' + CAMUNDA_MODEL_NS + '}resultVariable')

        return MessageEventDefinition(message,payload,resultVar=resultVar)


    def get_signal_event_definition(self, signalEventDefinition):
        """
        Parse the signalEventDefinition node and return an instance of
        SignalEventDefinition
        """

        message = signalEventDefinition.get(
            'signalRef') if signalEventDefinition is not None else self.node.get('name')
        # camunda doesn't have payload for signals evidently
        #payload = signalEventDefinition.attrib.get('{'+ CAMUNDA_MODEL_NS +'}expression')
        return SignalEventDefinition(message)

    def get_cancel_event_definition(self, cancelEventDefinition):
        """
        Parse the cancelEventDefinition node and return an instance of
        cancelEventDefinition
        """

        message = cancelEventDefinition.get(
            'cancelRef') if cancelEventDefinition is not None else self.node.get('name')
        # camunda doesn't have payload for cancels evidently
        #payload = cancelEventDefinition.attrib.get('{'+ CAMUNDA_MODEL_NS +'}expression')
        return CancelEventDefinition(message)



class BoundaryEventParser(IntermediateCatchEventParser):
    """
    Parse a Catching Boundary Event. This extends the
    IntermediateCatchEventParser in order to parse the event definition.
    """

    def create_task(self):
        event_definition = self.get_event_definition()
        # BPMN spec states that cancelActivity is True by default
        cancel_activity = self.node.get(
            'cancelActivity', default='true').lower() == 'true'
        return self.spec_class(self.spec, self.get_task_spec_name(),
                               cancel_activity=cancel_activity,
                               event_definition=event_definition,
                               description=self.node.get('name', None))
