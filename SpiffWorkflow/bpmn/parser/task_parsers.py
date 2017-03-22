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
from .util import *
from ..specs.event_definitions import TimerEventDefinition, MessageEventDefinition
import xml.etree.ElementTree as ET


class StartEventParser(TaskParser):

    """
    Parses a Start Event, and connects it to the internal spec.start task.
    """

    def create_task(self):
        t = super(StartEventParser, self).create_task()
        self.spec.start.connect(t)
        return t

    def handles_multiple_outgoing(self):
        return True


class EndEventParser(TaskParser):

    """
    Parses and End Event. This also checks whether it should be a terminating end event.
    """

    def create_task(self):

        terminateEventDefinition = self.xpath(
            './/bpmn:terminateEventDefinition')
        task = self.spec_class(self.spec, self.get_task_spec_name(),
                               is_terminate_event=terminateEventDefinition, description=self.node.get('name', None))
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
    Base class for parsing Manual Tasks. Currently assumes that Manual Tasks should be treated the same way as User Tasks.
    """
    pass


class NoneTaskParser(UserTaskParser):

    """
    Base class for parsing unspecified Tasks. Currently assumes that such Tasks should be treated the same way as User Tasks.
    """
    pass


class ExclusiveGatewayParser(TaskParser):

    """
    Parses an Exclusive Gateway, setting up the outgoing conditions appropriately.
    """

    def connect_outgoing(self, outgoing_task, outgoing_task_node, sequence_flow_node, is_default):
        if is_default:
            super(ExclusiveGatewayParser, self).connect_outgoing(
                outgoing_task, outgoing_task_node, sequence_flow_node, is_default)
        else:
            cond = self.parser._parse_condition(
                outgoing_task, outgoing_task_node, sequence_flow_node, task_parser=self)
            if cond is None:
                raise ValidationException(
                    'Non-default exclusive outgoing sequence flow without condition', sequence_flow_node, self.process_parser.filename)
            self.task.connect_outgoing_if(cond, outgoing_task, sequence_flow_node.get('id'), sequence_flow_node.get(
                'name', None), self.parser._parse_documentation(sequence_flow_node, task_parser=self))

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
        At the moment I haven't implemented support for diverging inclusive gateways
        """
        return False


class CallActivityParser(TaskParser):

    """
    Parses a CallActivity node. This also supports the not-quite-correct BPMN that Signavio produces (which does not have a calledElement attribute).
    """

    def create_task(self):
        wf_spec = self.get_subprocess_parser().get_spec()
        return self.spec_class(self.spec, self.get_task_spec_name(), bpmn_wf_spec=wf_spec, bpmn_wf_class=self.parser.WORKFLOW_CLASS, description=self.node.get('name', None))

    def get_subprocess_parser(self):
        calledElement = self.node.get('calledElement', None)
        if not calledElement:
            raise ValidationException(
                'No "calledElement" attribute for Call Activity.', node=self.node, filename=self.process_parser.filename)
        return self.parser.get_process_parser(calledElement)


class ScriptTaskParser(TaskParser):

    """
    Parses a script task
    """

    def create_task(self):
        script = self.get_script()
        return self.spec_class(self.spec, self.get_task_spec_name(), script, description=self.node.get('name', None))

    def get_script(self):
        """
        Gets the script content from the node. A subclass can override this method, if the script needs
        to be pre-parsed. The result of this call will be passed to the Script Engine for execution.
        """
        return one(self.xpath('.//bpmn:script')).text


class IntermediateCatchEventParser(TaskParser):

    """
    Parses an Intermediate Catch Event. This currently onlt supports Message and Timer event definitions.
    """

    def create_task(self):
        event_definition = self.get_event_definition()
        return self.spec_class(self.spec, self.get_task_spec_name(), event_definition, description=self.node.get('name', None))

    def get_event_definition(self):
        """
        Parse the event definition node, and return an instance of Event
        """
        messageEventDefinition = first(
            self.xpath('.//bpmn:messageEventDefinition'))
        if messageEventDefinition is not None:
            return self.get_message_event_definition(messageEventDefinition)

        timerEventDefinition = first(
            self.xpath('.//bpmn:timerEventDefinition'))
        if timerEventDefinition is not None:
            return self.get_timer_event_definition(timerEventDefinition)

        raise NotImplementedError(
            'Unsupported Intermediate Catch Event: %r', ET.tostring(self.node))

    def get_message_event_definition(self, messageEventDefinition):
        """
        Parse the messageEventDefinition node and return an instance of MessageEventDefinition
        """
        messageRef = first(self.xpath('.//bpmn:messageRef'))
        message = messageRef.get(
            'name') if messageRef is not None else self.node.get('name')
        return MessageEventDefinition(message)

    def get_timer_event_definition(self, timerEventDefinition):
        """
        Parse the timerEventDefinition node and return an instance of TimerEventDefinition

        This currently only supports the timeDate node for specifying an expiry time for the timer.
        """
        timeDate = first(self.xpath('.//bpmn:timeDate'))
        return TimerEventDefinition(self.node.get('name', timeDate.text), self.parser.parse_condition(timeDate.text, None, None, None, None, self))


class BoundaryEventParser(IntermediateCatchEventParser):

    """
    Parse a Catching Boundary Event. This extends the IntermediateCatchEventParser in order to parse the event definition.
    """

    def create_task(self):
        event_definition = self.get_event_definition()
        cancel_activity = self.node.get(
            'cancelActivity', default='false').lower() == 'true'
        return self.spec_class(self.spec, self.get_task_spec_name(), cancel_activity=cancel_activity, event_definition=event_definition, description=self.node.get('name', None))
