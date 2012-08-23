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

class Parser(object):

    EXCLUSIVE_GATEWAY = full_tag('exclusiveGateway')

    def __init__(self, f):
        self.doc = etree.parse(f)
        self.xpath = xpath_eval(self.doc)
        self.spec = WorkflowSpec()

    def parse_node(self,node):

        if node.tag == self.EXCLUSIVE_GATEWAY:
            t = ExclusiveChoice(self.spec, node.get('id'), desciption=node.get('name', None))

        else:
            t = Simple(self.spec, node.get('id'), desciption=node.get('name', None))

        children = set()
        nxpath = xpath_eval(node)
        outgoing = nxpath('./bpmn2:outgoing')
        for sequence_flow_id in outgoing:
            sequence_flow = one(self.xpath('//bpmn2:sequenceFlow[@id="%s"]' % sequence_flow_id.text))
            target_ref = sequence_flow.get('targetRef')
            c = self.spec.task_specs.get(target_ref, None)
            if c is None:
                target_node = one(self.xpath('//bpmn2:*[@id="%s"]' % target_ref))
                c = self.parse_node(target_node)
            children.add(c)

        for c in children:
            if isinstance(t, ExclusiveChoice):
                cond = Equal(Attrib('status'), 'Approve')
                t.connect_if(cond, c)
            else:
                t.connect(c)

        if isinstance(t, ExclusiveChoice):
            t.connect(children.pop())

        return t

    def parse(self):


        start_node = one(self.xpath('//bpmn2:startEvent'))
        start_task = self.parse_node(start_node)
        start_task.follow(self.spec.start)


def main():
    f = open('/home/matth/workspace_bpmn/MOC/stage_1.bpmn', 'r')
    with(f):
        p = Parser(f)
        p.parse()
        Workflow(p.spec).dump()

if __name__ == '__main__':
    main()