# Copyright (C) 2012 Matthew Hampton
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

from .ValidationException import ValidationException
from ..specs.bpmn_process_spec import BpmnProcessSpec
from ..specs.data_spec import DataObject
from ..specs.control import StartEventJoin, StartEventSplit
from .node_parser import NodeParser
from .util import first


class ProcessParser(NodeParser):
    """
    Parses a single BPMN process, including all of the tasks within that
    process.
    """

    def __init__(self, p, node, nsmap, data_stores, filename=None, lane=None):
        """
        Constructor.

        :param p: the owning BpmnParser instance
        :param node: the XML node for the process
        :param data_stores: map of ids to data store implementations
        :param filename: the source BPMN filename (optional)
        :param lane: the lane of a subprocess (optional)
        """
        super().__init__(node, nsmap, filename=filename, lane=lane)
        self.parser = p
        self.lane = lane
        self.spec = None
        self.process_executable = node.get('isExecutable', 'true') == 'true'
        self.data_stores = data_stores
        self.parent = None

    def get_name(self):
        """
        Returns the process name (or ID, if no name is included in the file)
        """
        return self.node.get('name', default=self.bpmn_id)

    def has_lanes(self) -> bool:
        """Returns true if this process has one or more named lanes """
        elements = self.xpath("//bpmn:lane")
        for el in elements:
            if el.get("name"):
                return True
        return False

    def start_messages(self):
        """ This returns a list of message names that would cause this
            process to start. """
        message_names = []
        messages = self.xpath("//bpmn:message")
        message_event_definitions = self.xpath(
            "//bpmn:startEvent/bpmn:messageEventDefinition")
        for message_event_definition in message_event_definitions:
            message_model_identifier = message_event_definition.attrib.get(
                "messageRef"
            )
            if message_model_identifier is None:
                raise ValidationException(
                    f"Could not find messageRef from message event definition: {message_event_definition}"
                )
            # Convert the id into a Message Name
            message_name = next((m for m in messages if m.attrib.get('id') == message_model_identifier), None)
            message_names.append(message_name.attrib.get('name'))

        return message_names

    def called_element_ids(self):
        """
        Returns a list of ids referenced by `bpmn:callActivity` nodes.
        """
        return self.xpath(".//bpmn:callActivity/@calledElement")

    def parse_node(self, node):
        """
        Parses the specified child task node, and returns the task spec. This
        can be called by a TaskParser instance, that is owned by this
        ProcessParser.
        """
        if node.get('id') in self.spec.task_specs:
            return self.spec.task_specs[node.get('id')]

        (node_parser, spec_class) = self.parser._get_parser_class(node.tag)
        if not node_parser or not spec_class:
            raise ValidationException("There is no support implemented for this task type.",
                                      node=node, file_name=self.filename)
        np = node_parser(self, spec_class, node, self.nsmap, lane=self.lane)
        task_spec = np.parse_node()
        return task_spec

    def _parse(self):
        # here we only look in the top level, We will have another
        # bpmn:startEvent if we have a subworkflow task
        start_node_list = self.xpath('./bpmn:startEvent')
        if not start_node_list and self.process_executable:
            raise ValidationException("No start event found", node=self.node, file_name=self.filename)
        if not self.process_executable:
            raise ValidationException(f"Process {self.bpmn_id} is not executable.", node=self.node, file_name=self.filename)
        self.spec = BpmnProcessSpec(name=self.bpmn_id, description=self.get_name(), filename=self.filename)

        # Get the data objects
        for obj in self.xpath('./bpmn:dataObject'):
            data_object = self.parse_data_object(obj)
            self.spec.data_objects[data_object.bpmn_id] = data_object

        # Check for an IO Specification.
        io_spec = first(self.xpath('./bpmn:ioSpecification'))
        if io_spec is not None:
            self.spec.io_specification = self.parse_io_spec()

        # set the data stores on the process spec so they can survive
        # serialization
        self.spec.data_stores = self.data_stores
        for node in start_node_list:
            self.parse_node(node)

        if len(start_node_list) > 1:
            split_task = StartEventSplit(self.spec, 'StartEventSplit')
            join_task = StartEventJoin(self.spec, 'StartEventJoin', split_task='StartEventSplit', threshold=1, cancel=True)
            for spec in self.spec.start.outputs:
                spec.inputs = [split_task]
                spec.connect(join_task)
            split_task.outputs = self.spec.start.outputs
            self.spec.start.outputs = [split_task]
            split_task.inputs = [self.spec.start]

    def parse_data_object(self, obj):
        return self.create_data_spec(obj, DataObject)

    def get_spec(self):
        """
        Parse this process (if it has not already been parsed), and return the
        workflow spec.
        """
        if self.spec is None:
            self._parse()
        return self.spec
