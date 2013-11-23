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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from SpiffWorkflow.bpmn.specs.BpmnProcessSpec import BpmnProcessSpec
from SpiffWorkflow.bpmn.parser.util import *

class ProcessParser(object):
    """
    Parses a single BPMN process, including all of the tasks within that process.
    """

    def __init__(self, p, node, svg=None, filename=None, doc_xpath=None):
        """
        Constructor.

        :param p: the owning BpmnParser instance
        :param node: the XML node for the process
        :param svg: the SVG representation of this process as a string (optional)
        :param filename: the source BPMN filename (optional)

        """
        self.parser = p
        self.node = node
        self.doc_xpath = doc_xpath
        self.xpath = xpath_eval(node)
        self.spec = BpmnProcessSpec(name=self.get_id(), description=self.get_name(), svg=svg, filename=filename)
        self.parsing_started = False
        self.is_parsed = False
        self.parsed_nodes = {}
        self.svg = svg
        self.filename = filename
        self.id_to_lane_lookup = None
        self._init_lane_lookup()

    def get_id(self):
        """
        Returns the process ID
        """
        return self.node.get('id')

    def get_name(self):
        """
        Returns the process name (or ID, if no name is included in the file)
        """
        return self.node.get('name', default=self.get_id())

    def parse_node(self,node):
        """
        Parses the specified child task node, and returns the task spec.
        This can be called by a TaskParser instance, that is owned by this ProcessParser.
        """

        if node.get('id') in self.parsed_nodes:
            return self.parsed_nodes[node.get('id')]

        (node_parser, spec_class) = self.parser._get_parser_class(node.tag)
        if not node_parser or not spec_class:
            raise ValidationException("There is no support implemented for this task type.", node=node, filename=self.filename)
        np = node_parser(self, spec_class, node)
        task_spec = np.parse_node()

        return task_spec

    def get_lane(self, id):
        """
        Return the name of the lane that contains the specified task
        """
        return self.id_to_lane_lookup.get(id, None)

    def _init_lane_lookup(self):
        self.id_to_lane_lookup = {}
        for lane in self.xpath('.//bpmn:lane'):
            name = lane.get('name')
            if name:
                for ref in xpath_eval(lane)('bpmn:flowNodeRef'):
                    id = ref.text
                    if id:
                        self.id_to_lane_lookup[id] = name

    def _parse(self):
        start_node_list = self.xpath('.//bpmn:startEvent')
        if not start_node_list:
            raise ValidationException("No start event found", node=self.node, filename=self.filename)
        elif len(start_node_list) != 1:
            raise ValidationException("Only one Start Event is supported in each process", node=self.node, filename=self.filename)
        self.parsing_started = True
        self.parse_node(start_node_list[0])
        self.is_parsed = True

    def get_spec(self):
        """
        Parse this process (if it has not already been parsed), and return the workflow spec.
        """
        if self.is_parsed:
            return self.spec
        if self.parsing_started:
            raise NotImplementedError('Recursive call Activities are not supported.')
        self._parse()
        return self.get_spec()
