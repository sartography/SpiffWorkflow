from SpiffWorkflow.bpmn2.specs.ExclusiveGateway import ExclusiveGateway
from SpiffWorkflow.bpmn2.specs.ManualTask import ManualTask
from SpiffWorkflow.bpmn2.specs.UserTask import UserTask
from SpiffWorkflow.operators import Equal, Attrib
from SpiffWorkflow.specs.StartTask import StartTask
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec
from SpiffWorkflow.bpmn2.specs.EndEvent import EndEvent


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

def xpath_eval(node):
    namespaces = {'bpmn2':BPMN2_NS}
    return etree.XPathEvaluator(node, namespaces=namespaces)

def full_tag(tag):
    return '{%s}%s' % (BPMN2_NS, tag)


class TaskParser(object):

    def __init__(self, process_parser, spec_class, node):
        self.process_parser = process_parser
        self.spec_class = spec_class
        self.process_xpath = self.process_parser.xpath
        self.root_xpath = self.process_parser.parser.xpath
        self.spec = self.process_parser.parser.spec
        self.node = node
        self.xpath = xpath_eval(node)

    def parse_node(self):

        self.task = self.create_task()

        children = []
        outgoing = self.process_xpath('.//bpmn2:sequenceFlow[@sourceRef="%s"]' % self.node.get('id'))
        for sequence_flow in outgoing:
            target_ref = sequence_flow.get('targetRef')
            target_node = one(self.process_xpath('.//bpmn2:*[@id="%s"]' % target_ref))
            c = self.spec.task_specs.get(target_ref, None)
            if c is None:
                c = self.process_parser.parse_node(target_node)
            children.append((c, target_node, sequence_flow))

        for (c, target_node, sequence_flow) in children:
            self.connect_outgoing(c, target_node, sequence_flow)

        return self.task

    def create_task(self):
        return self.spec_class(self.spec, self.node.get('id'), description=self.node.get('name', None))

    def connect_outgoing(self, outgoing_task, outgoing_task_node, sequence_flow_node):
        self.task.connect_outgoing(outgoing_task, sequence_flow_node.get('name', None))

class StartEventParser(TaskParser):
    def create_task(self):
        return self.spec.start

    def connect_outgoing(self, outgoing_task, outgoing_task_node, sequence_flow_node):
        self.task.connect(outgoing_task)

class EndEventParser(TaskParser):
    pass

class UserTaskParser(TaskParser):
    pass

class ManualTaskParser(UserTaskParser):
    pass

class ExclusiveGatewayParser(TaskParser):

    def connect_outgoing(self, outgoing_task, outgoing_task_node, sequence_flow_node):

        if not self.task.outputs:
            #We need a default, it might as well be this one
            self.task.connect(outgoing_task)
        cond = self.create_condition(outgoing_task, outgoing_task_node, sequence_flow_node)
        self.task.connect_outgoing_if(cond, outgoing_task, sequence_flow_node.get('name', None))

    def create_condition(self, outgoing_task, outgoing_task_node, sequence_flow_node):
        return Equal(Attrib('choice'), sequence_flow_node.get('name', None))

class ProcessParser(object):

    PARSER_CLASSES = {
        full_tag('startEvent')          : (StartEventParser, StartTask),
        full_tag('endEvent')            : (EndEventParser, EndEvent),
        full_tag('userTask')            : (UserTaskParser, UserTask),
        full_tag('manualTask')          : (ManualTaskParser, ManualTask),
        full_tag('exclusiveGateway')    : (ExclusiveGatewayParser, ExclusiveGateway),
        }

    def __init__(self, p, node):
        self.parser = p
        self.doc = p.doc
        self.root_xpath = p.xpath
        self.node = node
        self.xpath = xpath_eval(node)

    def is_called(self):
        called_by = self.root_xpath('//bpmn2:callActivity[@calledElement="%s"]' % self.node.get('id'))
        return called_by and len(called_by) > 0

    def parse_node(self,node):
        (node_parser, spec_class) = self.PARSER_CLASSES[node.tag]
        return node_parser(self, spec_class, node).parse_node()

    def parse(self):
        start_node = one(self.xpath('.//bpmn2:startEvent'))
        self.parse_node(start_node)

class Parser(object):

    def __init__(self, f):
        self.doc = etree.parse(f)
        self.xpath = xpath_eval(self.doc)
        self.spec = WorkflowSpec()

    def parse(self):
        processes = self.xpath('//bpmn2:process')
        for process in processes:
            process_parser = ProcessParser(self, process)
            if not process_parser.is_called():
                process_parser.parse()


