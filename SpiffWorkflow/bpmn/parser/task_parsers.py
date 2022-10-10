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


class SubprocessParser:

    # Not really a fan of this, but I need a way of calling these methods from a task
    # parser that extends the base parser to override extension parsing.  I can't inherit
    # from my extended task parser AND the original subworkflow parsers because they
    # both inherit from the same base.

    @staticmethod
    def get_subprocess_spec(task_parser):

        workflow_start_event = task_parser.xpath('./bpmn:startEvent')
        workflow_end_event = task_parser.xpath('./bpmn:endEvent')
        if len(workflow_start_event) != 1:
            raise ValidationException(
                'Multiple Start points are not allowed in SubWorkflow Task',
                node=task_parser.node,
                filename=task_parser.filename)
        if len(workflow_end_event) == 0:
            raise ValidationException(
                'A SubWorkflow Must contain an End event',
                node=task_parser.node,
                filename=task_parser.filename)

        nsmap = DEFAULT_NSMAP.copy()
        nsmap['camunda'] = "http://camunda.org/schema/1.0/bpmn"
        nsmap['di'] = "http://www.omg.org/spec/DD/20100524/DI"

        # Create wrapper xml for the subworkflow
        for ns, val in nsmap.items():
            etree.register_namespace(ns, val)

        task_parser.process_parser.parser.create_parser(
            task_parser.node,
            doc_xpath=task_parser.doc_xpath,
            filename=task_parser.filename,
            lane=task_parser.lane
        )
        return task_parser.node.get('id')

    @staticmethod
    def get_call_activity_spec(task_parser):

        called_element = task_parser.node.get('calledElement', None)
        if not called_element:
            raise ValidationException(
                'No "calledElement" attribute for Call Activity.',
                node=task_parser.node,
                filename=task_parser.filename)
        parser = task_parser.process_parser.parser.get_process_parser(called_element)
        if parser is None:
            raise ValidationException(
                f"The process '{called_element}' was not found. Did you mean one of the following: "
                f"{', '.join(task_parser.process_parser.parser.get_process_ids())}?",
                node=task_parser.node,
                filename=task_parser.filename)
        return called_element


class SubWorkflowParser(TaskParser):

    def create_task(self):
        subworkflow_spec = SubprocessParser.get_subprocess_spec(self)
        return self.spec_class(
            self.spec, self.get_task_spec_name(), subworkflow_spec,
            lane=self.lane, position=self.position,
            description=self.node.get('name', None))


class CallActivityParser(TaskParser):
    """Parses a CallActivity node."""

    def create_task(self):
        subworkflow_spec = SubprocessParser.get_call_activity_spec(self)
        return self.spec_class(
            self.spec, self.get_task_spec_name(), subworkflow_spec,
            lane=self.lane, position=self.position,
            description=self.node.get('name', None))


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
                f"Invalid Script Task.  No Script Provided. " + str(ae),
                node=self.node, filename=self.filename)


class ServiceTaskParser(TaskParser):

    """
    Parses a ServiceTask node.
    """
    pass

