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

from lxml import etree

from .ValidationException import ValidationException
from .TaskParser import TaskParser
from .util import one, DEFAULT_NSMAP

CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'


class UserTaskParser(TaskParser):

    """
    Base class for parsing User Tasks
    """
    pass


class ManualTaskParser(UserTaskParser):

    """
    Base class for parsing Manual Tasks. Currently assumes that Manual Tasks
    should be treated the same way as User Tasks.
    """
    pass


class NoneTaskParser(UserTaskParser):

    """
    Base class for parsing unspecified Tasks. Currently assumes that such Tasks
    should be treated the same way as User Tasks.
    """
    pass


class ExclusiveGatewayParser(TaskParser):
    """
    Parses an Exclusive Gateway, setting up the outgoing conditions
    appropriately.
    """

    def connect_outgoing(self, outgoing_task, outgoing_task_node,
                         sequence_flow_node, is_default):
        if is_default:
            super(ExclusiveGatewayParser, self).connect_outgoing(
                outgoing_task, outgoing_task_node, sequence_flow_node,
                is_default)
        else:
            cond = self.parse_condition(sequence_flow_node)
            if cond is None:
                raise ValidationException(
                    'Non-default exclusive outgoing sequence flow '
                    ' without condition',
                    sequence_flow_node,
                    self.filename)
            self.task.connect_outgoing_if(
                cond, outgoing_task,
                sequence_flow_node.get('id'),
                sequence_flow_node.get('name', None),
                self.parse_documentation(sequence_flow_node))

    def handles_multiple_outgoing(self):
        return True


class ParallelGatewayParser(TaskParser):

    """
    Parses a Parallel Gateway.
    """

    def handles_multiple_outgoing(self):
        return True


class InclusiveGatewayParser(TaskParser):

    """
    Parses an Inclusive Gateway.
    """

    def handles_multiple_outgoing(self):
        """
        At the moment I haven't implemented support for diverging inclusive
        gateways
        """
        return False


class SubWorkflowParser(TaskParser):

    """
    Base class for parsing unspecified Tasks. Currently assumes that such Tasks
    should be treated the same way as User Tasks.
    """
    def create_task(self):
        subworkflow_spec = self.get_subprocess_spec()
        return self.spec_class(
            self.spec, self.get_task_spec_name(), subworkflow_spec,
            lane=self.lane, position=self.position,
            description=self.node.get('name', None))

    def get_subprocess_spec(self):

        workflowStartEvent = self.xpath('./bpmn:startEvent')
        workflowEndEvent =  self.xpath('./bpmn:endEvent')
        if len(workflowStartEvent) != 1:
            raise ValidationException(
                'Multiple Start points are not allowed in SubWorkflow Task',
                node=self.node,
                filename=self.filename)
        if len(workflowEndEvent) == 0:
            raise ValidationException(
                'A SubWorkflow Must contain an End event',
                node=self.node,
                filename=self.filename)

        nsmap = DEFAULT_NSMAP.copy()
        nsmap['camunda'] = "http://camunda.org/schema/1.0/bpmn"
        nsmap['di'] = "http://www.omg.org/spec/DD/20100524/DI"

        # Create wrapper xml for the subworkflow
        for ns, val in nsmap.items():
            etree.register_namespace(ns, val)

        self.process_parser.parser.create_parser(
            self.node,
            doc_xpath=self.doc_xpath,
            filename=self.filename,
            lane=self.lane
        )
        return self.node.get('id')


class TransactionSubprocessParser(SubWorkflowParser):
    """Parses a transaction node"""

    def create_task(self):
        subworkflow_spec = self.get_subprocess_spec()
        return self.spec_class(
            self.spec, self.get_task_spec_name(), subworkflow_spec,
            position=self.position,
            description=self.node.get('name', None))


class CallActivityParser(TaskParser):
    """Parses a CallActivity node."""

    def create_task(self):
        subworkflow_spec = self.get_subprocess_spec()
        return self.spec_class(
            self.spec, self.get_task_spec_name(), subworkflow_spec,
            lane=self.lane, position=self.position,
            description=self.node.get('name', None))

    def get_subprocess_spec(self):
        called_element = self.node.get('calledElement', None)
        if not called_element:
            raise ValidationException(
                'No "calledElement" attribute for Call Activity.',
                node=self.node,
                filename=self.filename)
        parser = self.process_parser.parser.get_process_parser(called_element)
        if parser is None:
            raise ValidationException(
                f"The process '{called_element}' was not found. Did you mean one of the following: "
                f"{', '.join(self.process_parser.parser.get_process_ids())}?",
                node=self.node,
                filename=self.filename)
        return called_element


class ScriptTaskParser(TaskParser):
    """
    Parses a script task
    """

    def create_task(self):
        script = self.get_script()
        return self.spec_class(self.spec, self.get_task_spec_name(), script,
                               lane=self.lane,
                               position=self.position,
                               description=self.node.get('name', None))

    def get_script(self):
        """
        Gets the script content from the node. A subclass can override this
        method, if the script needs to be pre-parsed. The result of this call
        will be passed to the Script Engine for execution.
        """
        try:
            return one(self.xpath('.//bpmn:script')).text
        except AssertionError as ae:
            raise ValidationException(
                f"Invalid Script Task.  No Script Provided. ",
                node=self.node, filename=self.filename)
