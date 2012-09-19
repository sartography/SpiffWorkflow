from lxml import etree

__author__ = 'matth'

BPMN_MODEL_NS='http://www.omg.org/spec/BPMN/20100524/MODEL'
SIGNAVIO_NS='http://www.signavio.com'

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

def xpath_eval(node):
    namespaces = {'bpmn':BPMN_MODEL_NS, 'signavio':SIGNAVIO_NS}
    return etree.XPathEvaluator(node, namespaces=namespaces)

def full_tag(tag):
    return '{%s}%s' % (BPMN_MODEL_NS, tag)