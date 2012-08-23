from SpiffWorkflow.Workflow import Workflow
from SpiffWorkflow.operators import Equal, Attrib
from SpiffWorkflow.specs.ExclusiveChoice import ExclusiveChoice
from SpiffWorkflow.specs.Simple import Simple
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec

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

    def __init__(self, p, node):
        self.parser = p
        self.doc = p.doc
        self.root_xpath = p.xpath
        self.spec = p.spec
        self.node = node
        self.xpath = xpath_eval(node)

    def parse_node(self):

        self.task = self.create_task()

        children = set()
        child_nodes = {}
        outgoing = self.xpath('./bpmn2:outgoing')
        for sequence_flow_id in outgoing:
            sequence_flow = one(self.root_xpath('//bpmn2:sequenceFlow[@id="%s"]' % sequence_flow_id.text))
            target_ref = sequence_flow.get('targetRef')
            target_node = one(self.root_xpath('//bpmn2:*[@id="%s"]' % target_ref))
            c = self.spec.task_specs.get(target_ref, None)
            if c is None:
                c = self.parser.parse_node(target_node)
            children.add(c)
            child_nodes[target_ref] = (target_node, sequence_flow)

        for c in children:
            (target_node, sequence_flow) = child_nodes[c.name]
            self.connect_outgoing(c, target_node, sequence_flow)

        return self.task

    def create_task(self):
        return Simple(self.spec, self.node.get('id'), description=self.node.get('name', None))

    def connect_outgoing(self, outgoing_task, outgoing_task_node, sequence_flow_node):
        self.task.connect(outgoing_task)

class StartEventParser(TaskParser):
    def create_task(self):
        return self.spec.start

class ExclusiveGatewayParser(TaskParser):

    def create_task(self):
        return ExclusiveChoice(self.spec, self.node.get('id'), description=self.node.get('name', None))

    def connect_outgoing(self, outgoing_task, outgoing_task_node, sequence_flow_node):
        cond = Equal(Attrib('status'), 'Approve')
        if not self.task.outputs:
            #We need a default, it might as well be this one
            self.task.connect(outgoing_task)
        self.task.connect_if(cond, outgoing_task)


class Parser(object):

    START_EVENT = full_tag('startEvent')
    EXCLUSIVE_GATEWAY = full_tag('exclusiveGateway')

    PARSER_CLASSES = {
        START_EVENT : StartEventParser,
        EXCLUSIVE_GATEWAY: ExclusiveGatewayParser
    }

    def __init__(self, f):
        self.doc = etree.parse(f)
        self.xpath = xpath_eval(self.doc)
        self.spec = WorkflowSpec()


    def parse_node(self,node):

        return self.PARSER_CLASSES.get(node.tag, TaskParser)(self, node).parse_node()


    def parse(self):

        start_node = one(self.xpath('//bpmn2:startEvent'))
        start_task = self.parse_node(start_node)



def main():
    f = open('/home/matth/workspace_bpmn/MOC/stage_1.bpmn', 'r')
    with(f):
        p = Parser(f)
        p.parse()
        Workflow(p.spec).dump()

if __name__ == '__main__':
    main()