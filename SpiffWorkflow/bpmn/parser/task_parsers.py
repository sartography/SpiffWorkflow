from SpiffWorkflow.bpmn.BpmnWorkflow import BpmnCondition
from SpiffWorkflow.bpmn.specs.MessageEvent import MessageEvent
from SpiffWorkflow.bpmn.specs.TimerEvent import TimerEvent
from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser
from SpiffWorkflow.bpmn.parser.util import *

__author__ = 'matth'

from lxml import etree

class StartEventParser(TaskParser):
    def create_task(self):
        t = super(StartEventParser, self).create_task()
        self.spec.start.connect(t)
        return t

    def handles_multiple_outgoing(self):
        return True

class EndEventParser(TaskParser):

    def create_task(self):

        terminateEventDefinition = self.xpath('.//bpmn:terminateEventDefinition')
        task = self.spec_class(self.spec, self.get_task_spec_name(), is_terminate_event=terminateEventDefinition, description=self.node.get('name', None))
        task.connect_outgoing(self.spec.end, '%s.ToEndJoin'%self.node.get('id'), None)
        return task

class UserTaskParser(TaskParser):
    pass

class ManualTaskParser(UserTaskParser):
    pass

class ExclusiveGatewayParser(TaskParser):

    def connect_outgoing(self, outgoing_task, outgoing_task_node, sequence_flow_node, is_default):
        if is_default:
            super(ExclusiveGatewayParser, self).connect_outgoing(outgoing_task, outgoing_task_node, sequence_flow_node, is_default)
        else:
            cond = self.parser._parse_condition(outgoing_task, outgoing_task_node, sequence_flow_node)
            if cond is None:
                raise ValueError('Non-default exclusive outgoing sequence flow without condition')
            self.task.connect_outgoing_if(BpmnCondition(cond), outgoing_task, sequence_flow_node.get('id'), sequence_flow_node.get('name', None))

    def handles_multiple_outgoing(self):
        return True

    def is_parallel_branching(self):
        return False

class ParallelGatewayParser(TaskParser):
    def handles_multiple_outgoing(self):
        return True

class CallActivityParser(TaskParser):
    def create_task(self):
        wf_spec = self.get_subprocess_parser().get_spec()
        return self.spec_class(self.spec, self.get_task_spec_name(), wf_spec=wf_spec, wf_class=self.parser.WORKFLOW_CLASS, description=self.node.get('name', None))

    def is_parallel_branching(self):
        return self.get_subprocess_parser().is_parallel_branching

    def get_subprocess_parser(self):
        calledElement = self.node.get('calledElement', None)
        if not calledElement:
            signavioMetaData = self.xpath('.//signavio:signavioMetaData[@metaKey="entry"]')
            if not signavioMetaData:
                raise ValueError('No "calledElement" attribute or Signavio "Subprocess reference" present.' )
            calledElement = one(signavioMetaData).get('metaValue')
        return self.parser.get_process_parser(calledElement)

class ScriptTaskParser(TaskParser):
    def create_task(self):
        script = self.get_script()
        return self.spec_class(self.spec, self.get_task_spec_name(), script, description=self.node.get('name', None))

    def get_script(self):
        return one(self.xpath('.//bpmn:script')).text

class IntermediateCatchEventParser(TaskParser):
    def create_task(self):
        event_spec = self.get_event_spec()
        return self.spec_class(self.spec, self.get_task_spec_name(), event_spec, description=self.node.get('name', None))

    def get_event_spec(self):
        messageEventDefinition = first(self.xpath('.//bpmn:messageEventDefinition'))
        if messageEventDefinition is not None:
            return self.get_message_event_spec(messageEventDefinition)

        timerEventDefinition = first(self.xpath('.//bpmn:timerEventDefinition'))
        if timerEventDefinition is not None:
            return self.get_timer_event_spec(timerEventDefinition)

        raise NotImplementedError('Unsupported Intermediate Catch Event: %r', etree.tostring(self.node) )

    def get_message_event_spec(self, messageEventDefinition):
        messageRef = first(self.xpath('.//bpmn:messageRef'))
        message = messageRef.get('name') if messageRef is not None else self.node.get('name')
        return MessageEvent(message)

    def get_timer_event_spec(self, timerEventDefinition):
        timeDate = first(self.xpath('.//bpmn:timeDate'))
        return TimerEvent(self.node.get('name', timeDate.text), timeDate.text)


class BoundaryEventParser(IntermediateCatchEventParser):
    def create_task(self):
        event_spec = self.get_event_spec()
        cancel_activity = self.node.get('cancelActivity', default='false').lower() == 'true'
        return self.spec_class(self.spec, self.get_task_spec_name(), cancel_activity=cancel_activity, event_spec=event_spec, description=self.node.get('name', None))
