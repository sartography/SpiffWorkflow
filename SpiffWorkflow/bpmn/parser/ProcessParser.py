# -*- coding: utf-8 -*-
from builtins import object
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
from ..specs.BpmnProcessSpec import BpmnProcessSpec
from .util import xpath_eval, DIAG_COMMON_NS


class ProcessParser(object):
    """
    Parses a single BPMN process, including all of the tasks within that
    process.
    """

    def __init__(self, p, node, filename=None, doc_xpath=None, current_lane=None):
        """
        Constructor.

        :param p: the owning BpmnParser instance
        :param node: the XML node for the process
        :param filename: the source BPMN filename (optional)
        """
        self.parser = p
        self.node = node
        self.filename = filename
        self.doc_xpath = doc_xpath
        self.xpath = xpath_eval(node)
        self.parsed_nodes = {}
        self.id_to_lane_lookup = self._init_lane_lookup()
        self.id_to_coords_lookup = self._init_coord_lookup()
        self.current_lane = current_lane
        self.spec = None

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
            raise ValidationException(
                "There is no support implemented for this task type.",
                node=node, filename=self.filename)
        np = node_parser(self, spec_class, node)
        task_spec = np.parse_node()

        return task_spec

    def get_lane(self, id):
        """
        Return the name of the lane that contains the specified task
        As we may be in a sub_process, adopt the current_lane if we
        have no lane ourselves.  In the future we might consider supporting
        being in two lanes at once.
        """
        lane = self.id_to_lane_lookup.get(id, None)
        if lane:
            return lane
        else:
            return self.current_lane

    def _init_lane_lookup(self):
        id_to_lane_lookup = {}
        for lane in self.xpath('.//bpmn:lane'):
            name = lane.get('name')
            if name:
                for ref in xpath_eval(lane)('bpmn:flowNodeRef'):
                    id = ref.text
                    if id:
                        id_to_lane_lookup[id] = name
        return id_to_lane_lookup

    def get_coord(self, id):
        """
        Return the x,y coordinates of the given task, if available.
        """
        return self.id_to_coords_lookup.get(id, {'x':0, 'y':0})

    def _init_coord_lookup(self):
        """Creates a lookup table with the x/y coordinates of each shape.
        Only tested with the output from the Camunda modeler, which provides
        these details in the bpmndi / and dc namespaces."""
        id_to_coords_lookup = {}
        for position in self.doc_xpath('.//bpmndi:BPMNShape'):
            bounds = xpath_eval(position)("dc:Bounds")
            if len(bounds) > 0 and 'bpmnElement' in position.attrib:
                bound = bounds[0]
                id_to_coords_lookup[position.attrib['bpmnElement']] = \
                    {'x': float(bound.attrib['x']), 'y': float(bound.attrib['y'])}
        return id_to_coords_lookup

    def _parse(self):
        # here we only look in the top level, We will have another
        # bpmn:startEvent if we have a subworkflow task
        start_node_list = self.xpath('./bpmn:startEvent')
        if not start_node_list:
            raise ValidationException(
                "No start event found", node=self.node, filename=self.filename)
        self.spec = BpmnProcessSpec(name=self.get_id(), description=self.get_name(), filename=self.filename)
        for node in start_node_list:
            self.parse_node(node)

    def get_spec(self):
        """
        Parse this process (if it has not already been parsed), and return the
        workflow spec.
        """
        if self.spec is None:
            self._parse()
        return self.spec
