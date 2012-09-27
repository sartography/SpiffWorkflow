from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from SpiffWorkflow.bpmn.specs.MessageEvent import MessageEvent
from SpiffWorkflow.bpmn.specs.TimerEvent import TimerEvent
from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser
from SpiffWorkflow.bpmn.parser.util import *

__author__ = 'matth'

from lxml import etree

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

        terminateEventDefinition = self.xpath('.//bpmn:terminateEventDefinition')
        task = self.spec_class(self.spec, self.get_task_spec_name(), is_terminate_event=terminateEventDefinition, description=self.node.get('name', None))
        task.connect_outgoing(self.spec.end, '%s.ToEndJoin'%self.node.get('id'), None, None)
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
            super(ExclusiveGatewayParser, self).connect_outgoing(outgoing_task, outgoing_task_node, sequence_flow_node, is_default)
        else:
            cond = self.parser._parse_condition(outgoing_task, outgoing_task_node, sequence_flow_node)
            if cond is None:
                raise ValidationException('Non-default exclusive outgoing sequence flow without condition', sequence_flow_node, self.process_parser.filename)
            self.task.connect_outgoing_if(cond, outgoing_task, sequence_flow_node.get('id'), sequence_flow_node.get('name', None), self.parser._parse_documentation(sequence_flow_node))

    def handles_multiple_outgoing(self):
        return True

class ParallelGatewayParser(TaskParser):
    """
    Parses a Parallel Gateway.
    """

    def handles_multiple_outgoing(self):
        return True

class CallActivityParser(TaskParser):
    """
    Parses a CallActivity node. This also supports the not-quite-correct BPMN that Signavio produces (which does not have a calledElement attribute).
    """

    def create_task(self):
        wf_spec = self.get_subprocess_parser().get_spec()
        return self.spec_class(self.spec, self.get_task_spec_name(), wf_spec=wf_spec, wf_class=self.parser.WORKFLOW_CLASS, description=self.node.get('name', None))

    def get_subprocess_parser(self):
        calledElement = self.node.get('calledElement', None)
        if not calledElement:
            raise ValidationException('No "calledElement" attribute for Call Activity.', node=self.node, filename=self.process_parser.filename)
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
        event_spec = self.get_event_spec()
        return self.spec_class(self.spec, self.get_task_spec_name(), event_spec, description=self.node.get('name', None))

    def get_event_spec(self):
        """
        Parse the event definition node, and return an instance of Event
        """
        messageEventDefinition = first(self.xpath('.//bpmn:messageEventDefinition'))
        if messageEventDefinition is not None:
            return self.get_message_event_spec(messageEventDefinition)

        timerEventDefinition = first(self.xpath('.//bpmn:timerEventDefinition'))
        if timerEventDefinition is not None:
            return self.get_timer_event_spec(timerEventDefinition)

        raise NotImplementedError('Unsupported Intermediate Catch Event: %r', etree.tostring(self.node) )

    def get_message_event_spec(self, messageEventDefinition):
        """
        Parse the messageEventDefinition node and return an instance of MessageEvent
        """
        messageRef = first(self.xpath('.//bpmn:messageRef'))
        message = messageRef.get('name') if messageRef is not None else self.node.get('name')
        return MessageEvent(message)

    def get_timer_event_spec(self, timerEventDefinition):
        """
        Parse the timerEventDefinition node and return an instance of TimerEvent

        This currently only supports the timeDate node for specifying an expiry time for the timer.
        """
        timeDate = first(self.xpath('.//bpmn:timeDate'))
        return TimerEvent(self.node.get('name', timeDate.text), timeDate.text)


class BoundaryEventParser(IntermediateCatchEventParser):
    """
    Parse a Catching Boundary Event. This extends the IntermediateCatchEventParser in order to parse the event definition.
    """

    def create_task(self):
        event_spec = self.get_event_spec()
        cancel_activity = self.node.get('cancelActivity', default='false').lower() == 'true'
        return self.spec_class(self.spec, self.get_task_spec_name(), cancel_activity=cancel_activity, event_spec=event_spec, description=self.node.get('name', None))
