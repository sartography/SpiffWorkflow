import glob
import os
from SpiffWorkflow.bpmn.BpmnWorkflow import BpmnCondition, BpmnWorkflow
from SpiffWorkflow.bpmn.specs.BoundaryEvent import BoundaryEvent, BoundaryEventParent
from SpiffWorkflow.bpmn.specs.BpmnProcessSpec import BpmnProcessSpec
from SpiffWorkflow.bpmn.specs.CallActivity import CallActivity
from SpiffWorkflow.bpmn.specs.ExclusiveGateway import ExclusiveGateway
from SpiffWorkflow.bpmn.specs.IntermediateCatchEvent import IntermediateCatchEvent
from SpiffWorkflow.bpmn.specs.ManualTask import ManualTask
from SpiffWorkflow.bpmn.specs.MessageEvent import MessageEvent
from SpiffWorkflow.bpmn.specs.ParallelGateway import ParallelGateway
from SpiffWorkflow.bpmn.specs.ScriptTask import ScriptTask
from SpiffWorkflow.bpmn.specs.StartEvent import StartEvent
from SpiffWorkflow.bpmn.specs.TimerEvent import TimerEvent
from SpiffWorkflow.bpmn.specs.UserTask import UserTask
from SpiffWorkflow.bpmn.specs.EndEvent import EndEvent


__author__ = 'matth'


from lxml import etree

def one(nodes,or_none=False):
    if not nodes and or_none:
        return None
    assert len(nodes) == 1, 'Expected 1 result. Received %d results.' % (len(nodes))
    return nodes[0]

def first(nodes):
    if len(nodes) >= 1:
        return nodes[0]
    else:
        return None

BPMN2_NS='http://www.omg.org/spec/BPMN/20100524/MODEL'
SIGNAVIO_NS='http://www.signavio.com'

def xpath_eval(node):
    namespaces = {'bpmn2':BPMN2_NS, 'signavio':SIGNAVIO_NS}
    return etree.XPathEvaluator(node, namespaces=namespaces)

def full_tag(tag):
    return '{%s}%s' % (BPMN2_NS, tag)


class TaskParser(object):

    def __init__(self, process_parser, spec_class, node):
        self.parser = process_parser.parser
        self.process_parser = process_parser
        self.spec_class = spec_class
        self.process_xpath = self.process_parser.xpath
        self.spec = self.process_parser.spec
        self.node = node
        self.xpath = xpath_eval(node)

    def parse_node(self):

        self.task = self.create_task()

        boundary_event_nodes = self.process_xpath('.//bpmn2:boundaryEvent[@attachedToRef="%s"]' % self.get_id())
        if boundary_event_nodes:
            parent_task = BoundaryEventParent(self.spec, '%s.BoundaryEventParent' % self.get_id(), self.task, lane=self.task.lane)
            self.process_parser.parsed_nodes[self.node.get('id')] = parent_task

            parent_task.connect_outgoing(self.task, '%s.FromBoundaryEventParent' % self.get_id(), None)
            for boundary_event in boundary_event_nodes:
                b = self.process_parser.parse_node(boundary_event)
                parent_task.connect_outgoing(b, '%s.FromBoundaryEventParent' % boundary_event.get('id'), None)
        else:
            self.process_parser.parsed_nodes[self.node.get('id')] = self.task


        children = []
        outgoing = self.process_xpath('.//bpmn2:sequenceFlow[@sourceRef="%s"]' % self.get_id())
        if len(outgoing) > 1 and not self.handles_multiple_outgoing():
            raise NotImplementedError('Multiple outgoing flows are not supported for tasks of type %s', self.spec_class.__name__)
        for sequence_flow in outgoing:
            target_ref = sequence_flow.get('targetRef')
            target_node = one(self.process_xpath('.//bpmn2:*[@id="%s"]' % target_ref))
            c = self.process_parser.parse_node(target_node)
            children.append((c, target_node, sequence_flow))

        if children:
            default_outgoing = self.node.get('default')
            if not default_outgoing:
                (c, target_node, sequence_flow) = children[0]
                default_outgoing = sequence_flow.get('id')

            for (c, target_node, sequence_flow) in children:
                self.connect_outgoing(c, target_node, sequence_flow, sequence_flow.get('id') == default_outgoing)

        return parent_task if boundary_event_nodes else self.task

    def get_lane(self):
        lane_match = self.process_xpath('.//bpmn2:lane/bpmn2:flowNodeRef[text()="%s"]/..' % self.get_id())
        assert len(lane_match)<= 1
        return lane_match[0].get('name') if lane_match else None


    def get_task_spec_name(self, target_ref=None):
        return '%s.%s' %(self.process_parser.get_id(), target_ref or self.get_id())

    def get_id(self):
        return self.node.get('id')

    def create_task(self):
        return self.spec_class(self.spec, self.get_task_spec_name(), lane=self.get_lane(), description=self.node.get('name', None))

    def connect_outgoing(self, outgoing_task, outgoing_task_node, sequence_flow_node, is_default):
        self.task.connect_outgoing(outgoing_task, sequence_flow_node.get('id'), sequence_flow_node.get('name', None))

    def handles_multiple_outgoing(self):
        return False

    def is_parallel_branching(self):
        return len(self.task.outputs) > 1

class StartEventParser(TaskParser):
    def create_task(self):
        t = super(StartEventParser, self).create_task()
        self.spec.start.connect(t)
        return t

    def handles_multiple_outgoing(self):
        return True

class EndEventParser(TaskParser):

    def create_task(self):

        terminateEventDefinition = self.xpath('.//bpmn2:terminateEventDefinition')
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
        return one(self.xpath('.//bpmn2:script')).text

class IntermediateCatchEventParser(TaskParser):
    def create_task(self):
        event_spec = self.get_event_spec()
        return self.spec_class(self.spec, self.get_task_spec_name(), event_spec, description=self.node.get('name', None))

    def get_event_spec(self):
        messageEventDefinition = first(self.xpath('.//bpmn2:messageEventDefinition'))
        if messageEventDefinition is not None:
            return self.get_message_event_spec(messageEventDefinition)

        timerEventDefinition = first(self.xpath('.//bpmn2:timerEventDefinition'))
        if timerEventDefinition is not None:
            return self.get_timer_event_spec(timerEventDefinition)

        raise NotImplementedError('Unsupported Intermediate Catch Event: %r', etree.tostring(self.node) )

    def get_message_event_spec(self, messageEventDefinition):
        messageRef = first(self.xpath('.//bpmn2:messageRef'))
        message = messageRef.get('name') if messageRef is not None else self.node.get('name')
        return MessageEvent(message)

    def get_timer_event_spec(self, timerEventDefinition):
        timeDate = first(self.xpath('.//bpmn2:timeDate'))
        return TimerEvent(self.node.get('name', timeDate.text), timeDate.text)


class BoundaryEventParser(IntermediateCatchEventParser):
    def create_task(self):
        event_spec = self.get_event_spec()
        cancel_activity = self.node.get('cancelActivity', default='false').lower() == 'true'
        return self.spec_class(self.spec, self.get_task_spec_name(), cancel_activity=cancel_activity, event_spec=event_spec, description=self.node.get('name', None))

class ProcessParser(object):

    def __init__(self, p, node, svg):
        self.parser = p
        self.node = node
        self.xpath = xpath_eval(node)
        self.spec = BpmnProcessSpec(name=self.get_id(), description=self.get_name(), svg=svg)
        self.parsing_started = False
        self.is_parsed = False
        self.is_parallel_branching = False
        self.parsed_nodes = {}
        self.svg = svg

    def get_id(self):
        return self.node.get('id')

    def get_name(self):
        return self.node.get('name', default=self.get_id())

    def parse_node(self,node):
        if node.get('id') in self.parsed_nodes:
            return self.parsed_nodes[node.get('id')]

        (node_parser, spec_class) = self.parser.get_parser_class(node.tag)
        np = node_parser(self, spec_class, node)
        task_spec = np.parse_node()
        if np.is_parallel_branching():
            self.is_parallel_branching = True

        return task_spec

    def parse(self):
        start_node = one(self.xpath('.//bpmn2:startEvent'))
        self.parsing_started = True
        self.parse_node(start_node)
        self.spec._is_single_threaded = not self.is_parallel_branching
        self.is_parsed = True

    def get_spec(self):
        if self.is_parsed:
            return self.spec
        if self.parsing_started:
            raise NotImplementedError('Recursive call Activities are not supported.')
        self.parse()
        return self.get_spec()

class Parser(object):

    PARSER_CLASSES = {
        full_tag('startEvent')          : (StartEventParser, StartEvent),
        full_tag('endEvent')            : (EndEventParser, EndEvent),
        full_tag('userTask')            : (UserTaskParser, UserTask),
        full_tag('manualTask')          : (ManualTaskParser, ManualTask),
        full_tag('exclusiveGateway')    : (ExclusiveGatewayParser, ExclusiveGateway),
        full_tag('parallelGateway')     : (ParallelGatewayParser, ParallelGateway),
        full_tag('callActivity')        : (CallActivityParser, CallActivity),
        full_tag('scriptTask')                  : (ScriptTaskParser, ScriptTask),
        full_tag('intermediateCatchEvent')      : (IntermediateCatchEventParser, IntermediateCatchEvent),
        full_tag('boundaryEvent')               : (BoundaryEventParser, BoundaryEvent),
        }

    OVERRIDE_PARSER_CLASSES = {}

    WORKFLOW_CLASS = BpmnWorkflow

    def __init__(self):
        self.process_parsers = {}
        self.process_parsers_by_name = {}

    def get_parser_class(self, tag):
        if tag in self.OVERRIDE_PARSER_CLASSES:
            return self.OVERRIDE_PARSER_CLASSES[tag]
        else:
            return self.PARSER_CLASSES[tag]

    def get_process_parser(self, process_id_or_name):
        if process_id_or_name in self.process_parsers_by_name:
            return self.process_parsers_by_name[process_id_or_name]
        else:
            return self.process_parsers[process_id_or_name]

    def add_bpmn_file(self, filename):
        self.add_bpmn_files([filename])

    def add_bpmn_files_by_glob(self, g):
        self.add_bpmn_files(glob.glob(g))

    def add_bpmn_files(self, filenames):
        for filename in filenames:
            f = open(filename, 'r')
            try:
                xpath = xpath_eval(etree.parse(f))
            finally:
                f.close()

            svg = None
            if filename.endswith('.bpmn20.xml'):
                signavio_file = filename[:-len('.bpmn20.xml')] + '.signavio.xml'
                if os.path.exists(signavio_file):
                    f = open(signavio_file, 'r')
                    try:
                        signavio_tree = etree.parse(f)
                        svg_node = one(signavio_tree.xpath('.//svg-representation'))
                        svg = etree.fromstring(svg_node.text)
                    finally:
                        f.close()

            processes = xpath('//bpmn2:process')
            for process in processes:
                process_parser = ProcessParser(self, process, svg)
                if process_parser.get_id() in self.process_parsers:
                    raise ValueError('Duplicate processes with ID "%s"', process_parser.get_id())
                if process_parser.get_name() in self.process_parsers_by_name:
                    raise ValueError('Duplicate processes with name "%s"', process_parser.get_name())
                self.process_parsers[process_parser.get_id()] = process_parser
                self.process_parsers_by_name[process_parser.get_name()] = process_parser

    def _parse_condition(self, outgoing_task, outgoing_task_node, sequence_flow_node):
        xpath = xpath_eval(sequence_flow_node)
        condition_expression_node = conditionExpression = first(xpath('.//bpmn2:conditionExpression'))
        if conditionExpression is not None:
            conditionExpression = conditionExpression.text
        return self.parse_condition(conditionExpression, outgoing_task, outgoing_task_node, sequence_flow_node, condition_expression_node)

    def parse_condition(self, condition_expression, outgoing_task, outgoing_task_node, sequence_flow_node, condition_expression_node):
        return condition_expression

    def get_spec(self, process_id_or_name):
        return self.get_process_parser(process_id_or_name).get_spec()



