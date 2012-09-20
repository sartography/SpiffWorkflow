from SpiffWorkflow.bpmn.specs.BpmnProcessSpec import BpmnProcessSpec
from SpiffWorkflow.bpmn.parser.util import *

__author__ = 'matth'

class ProcessParser(object):

    def __init__(self, p, node, svg=None, filename=None):
        self.parser = p
        self.node = node
        self.xpath = xpath_eval(node)
        self.spec = BpmnProcessSpec(name=self.get_id(), description=self.get_name(), svg=svg, filename=filename)
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
        start_node = one(self.xpath('.//bpmn:startEvent'))
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



