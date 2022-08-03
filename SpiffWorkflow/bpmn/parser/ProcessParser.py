# -*- coding: utf-8 -*-

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
from ..specs.BpmnProcessSpec import BpmnMessageFlow, BpmnProcessSpec, BpmnDataSpecification
from .node_parser import NodeParser
from .util import first, xpath_eval


class ProcessParser(NodeParser):
    """
    Parses a single BPMN process, including all of the tasks within that
    process.
    """

    def __init__(self, p, node, filename=None, doc_xpath=None, lane=None):
        """
        Constructor.

        :param p: the owning BpmnParser instance
        :param node: the XML node for the process
        :param filename: the source BPMN filename (optional)
        :param doc_xpath: an xpath evaluator for the document (optional)
        :param lane: the lane of a subprocess (optional)
        """
        super().__init__(node, filename, doc_xpath, lane)
        self.parser = p
        self.parsed_nodes = {}
        self.lane = lane
        self.spec = None
        self.process_executable = True

    def get_name(self):
        """
        Returns the process name (or ID, if no name is included in the file)
        """
        return self.node.get('name', default=self.get_id())

    def parse_node(self, node):
        """
        Parses the specified child task node, and returns the task spec. This
        can be called by a TaskParser instance, that is owned by this
        ProcessParser.
        """

        if node.get('id') in self.parsed_nodes:
            return self.parsed_nodes[node.get('id')]

        (node_parser, spec_class) = self.parser._get_parser_class(node.tag)
        if not node_parser or not spec_class:
            raise ValidationException("There is no support implemented for this task type.",
                node=node, filename=self.filename)
        np = node_parser(self, spec_class, node, self.lane)
        task_spec = np.parse_node()
        return task_spec

    def _parse(self):
        # here we only look in the top level, We will have another
        # bpmn:startEvent if we have a subworkflow task
        self.process_executable = self.node.get('isExecutable', 'true') == 'true'
        start_node_list = self.xpath('./bpmn:startEvent')
        if not start_node_list and self.process_executable:
            raise ValidationException("No start event found", node=self.node, filename=self.filename)
        self.spec = BpmnProcessSpec(name=self.get_id(), description=self.get_name(), filename=self.filename)

        # Check for an IO Specification.
        io_spec = first(self.xpath('./bpmn:ioSpecification'))
        if io_spec is not None:
            data_parser = DataSpecificationParser(io_spec, self.filename, self.doc_xpath)
            self.spec.data_inputs, self.spec.data_outputs = data_parser.parse_io_spec()

        # Get the data objects
        for obj in self.xpath('./bpmn:dataObject'):
            data_parser = DataSpecificationParser(obj, self.filename, self.doc_xpath)
            data_object = data_parser.parse_data_object()
            self.spec.data_objects[data_object.name] = data_object

        for node in start_node_list:
            self.parse_node(node)

        participants = {}
        for node in self.doc_xpath('.//bpmn:participant'):
            if 'processRef' in node.attrib:
                participants[node.get('id')] = self.parser.get_spec(node.get('processRef'))

        for key in self.doc_xpath('.//bpmn:correlationKey'):
            self.spec.correlation_keys[key.get('name')] = [ prop.text for prop in key.getchildren() ]

        for item in self.doc_xpath('.//bpmn:messageFlow'):
            parser = MessageFlowParser(item, self.filename, self.doc_xpath, participants)
            flow = parser.parse()
            if flow.source_process == self.spec.name:
                self.spec.outgoing_message_flows.append(flow)
            if flow.target_process == self.spec.name:
                self.spec.incoming_message_flows.append(flow)

    def get_spec(self):
        """
        Parse this process (if it has not already been parsed), and return the
        workflow spec.
        """
        if self.spec is None:
            self._parse()
        return self.spec


class DataSpecificationParser(NodeParser):

    def parse_io_spec(self):
        inputs, outputs = [], []
        for elem in self.xpath('./bpmn:dataInput'):
            inputs.append(BpmnDataSpecification(elem.get('id'), elem.get('name')))
        for elem in self.xpath('./bpmn:dataOutput'):
            outputs.append(BpmnDataSpecification(elem.get('id'), elem.get('name')))
        return inputs, outputs

    def parse_data_object(self):
        return BpmnDataSpecification(self.node.get('id'), self.node.get('name'))


class MessageFlowParser(NodeParser):

    def __init__(self, node, filename, doc_xpath, participants):
        super().__init__(node, filename, doc_xpath)
        self.participants = participants

    def parse(self):
        source_proc, source_task, source_event_name = self.resolve_ref(self.node.get('sourceRef'))
        target_proc, target_task, target_event_name = self.resolve_ref(self.node.get('targetRef'))
        # If both events are present, they should be the same
        message_ref = source_event_name or target_event_name
        return BpmnMessageFlow(self.node.get('id'), message_ref, source_proc, target_proc, source_task, target_task)

    def resolve_ref(self, ref):
        if ref in self.participants:
            process, task, event_name = self.participants[ref], None, None
        else:
            for spec in self.participants.values():
                if ref in spec.task_specs:
                    process, task, event_name = spec, ref, spec.task_specs[ref].event_definition.name
                    break
        return process.name, task, event_name