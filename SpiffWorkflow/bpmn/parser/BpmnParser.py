# -*- coding: utf-8 -*-
from __future__ import division
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

import glob
from ..workflow import BpmnWorkflow
from .ValidationException import ValidationException
from ..specs.BoundaryEvent import BoundaryEvent
from ..specs.CallActivity import CallActivity
from ..specs.ExclusiveGateway import ExclusiveGateway
from ..specs.InclusiveGateway import InclusiveGateway
from ..specs.IntermediateCatchEvent import IntermediateCatchEvent
from ..specs.ManualTask import ManualTask
from ..specs.NoneTask import NoneTask
from ..specs.ParallelGateway import ParallelGateway
from ..specs.ScriptTask import ScriptTask
from ..specs.StartEvent import StartEvent
from ..specs.UserTask import UserTask
from ..specs.EndEvent import EndEvent
from .ProcessParser import ProcessParser
from .util import *
from .task_parsers import *
import xml.etree.ElementTree as ET


class BpmnParser(object):

    """
    The BpmnParser class is a pluggable base class that manages the parsing of a set of BPMN files.
    It is intended that this class will be overriden by an application that implements a BPMN engine.

    Extension points:
    OVERRIDE_PARSER_CLASSES provides a map from full BPMN tag name to a TaskParser and Task class.
    PROCESS_PARSER_CLASS provides a subclass of ProcessParser
    WORKFLOW_CLASS provides a subclass of BpmnWorkflow

    """

    PARSER_CLASSES = {
        full_tag('startEvent'): (StartEventParser, StartEvent),
        full_tag('endEvent'): (EndEventParser, EndEvent),
        full_tag('userTask'): (UserTaskParser, UserTask),
        full_tag('task'): (NoneTaskParser, NoneTask),
        full_tag('manualTask'): (ManualTaskParser, ManualTask),
        full_tag('exclusiveGateway'): (ExclusiveGatewayParser, ExclusiveGateway),
        full_tag('parallelGateway'): (ParallelGatewayParser, ParallelGateway),
        full_tag('inclusiveGateway'): (InclusiveGatewayParser, InclusiveGateway),
        full_tag('callActivity'): (CallActivityParser, CallActivity),
        full_tag('scriptTask'): (ScriptTaskParser, ScriptTask),
        full_tag('intermediateCatchEvent'): (IntermediateCatchEventParser, IntermediateCatchEvent),
        full_tag('boundaryEvent'): (BoundaryEventParser, BoundaryEvent),
    }

    OVERRIDE_PARSER_CLASSES = {}

    PROCESS_PARSER_CLASS = ProcessParser
    WORKFLOW_CLASS = BpmnWorkflow

    def __init__(self):
        """
        Constructor.
        """
        self.process_parsers = {}
        self.process_parsers_by_name = {}

    def _get_parser_class(self, tag):
        if tag in self.OVERRIDE_PARSER_CLASSES:
            return self.OVERRIDE_PARSER_CLASSES[tag]
        elif tag in self.PARSER_CLASSES:
            return self.PARSER_CLASSES[tag]
        return None, None

    def get_process_parser(self, process_id_or_name):
        """
        Returns the ProcessParser for the given process ID or name. It matches by name first.
        """
        if process_id_or_name in self.process_parsers_by_name:
            return self.process_parsers_by_name[process_id_or_name]
        else:
            return self.process_parsers[process_id_or_name]

    def add_bpmn_file(self, filename):
        """
        Add the given BPMN filename to the parser's set.
        """
        self.add_bpmn_files([filename])

    def add_bpmn_files_by_glob(self, g):
        """
        Add all filenames matching the provided pattern (e.g. *.bpmn) to the parser's set.
        """
        self.add_bpmn_files(glob.glob(g))

    def add_bpmn_files(self, filenames):
        """
        Add all filenames in the given list to the parser's set.
        """
        for filename in filenames:
            f = open(filename, 'r')
            try:
                self.add_bpmn_xml(ET.parse(f), filename=filename)
            finally:
                f.close()

    def add_bpmn_xml(self, bpmn, svg=None, filename=None):
        """
        Add the given lxml representation of the BPMN file to the parser's set.

        :param svg: Optionally, provide the text data for the SVG of the BPMN file
        :param filename: Optionally, provide the source filename.
        """
        xpath = xpath_eval(bpmn)

        processes = xpath('.//bpmn:process')
        for process in processes:
            process_parser = self.PROCESS_PARSER_CLASS(
                self, process, svg, filename=filename, doc_xpath=xpath)
            if process_parser.get_id() in self.process_parsers:
                raise ValidationException(
                    'Duplicate process ID', node=process, filename=filename)
            if process_parser.get_name() in self.process_parsers_by_name:
                raise ValidationException(
                    'Duplicate process name', node=process, filename=filename)
            self.process_parsers[process_parser.get_id()] = process_parser
            self.process_parsers_by_name[
                process_parser.get_name()] = process_parser

    def _parse_condition(self, outgoing_task, outgoing_task_node, sequence_flow_node, task_parser=None):
        xpath = xpath_eval(sequence_flow_node)
        condition_expression_node = conditionExpression = first(
            xpath('.//bpmn:conditionExpression'))
        if conditionExpression is not None:
            conditionExpression = conditionExpression.text
        return self.parse_condition(conditionExpression, outgoing_task, outgoing_task_node, sequence_flow_node, condition_expression_node, task_parser)

    def parse_condition(self, condition_expression, outgoing_task, outgoing_task_node, sequence_flow_node, condition_expression_node, task_parser):
        """
        Pre-parse the given condition expression, and return the parsed version. The returned version will be passed to the Script Engine
        for evaluation.
        """
        return condition_expression

    def _parse_documentation(self, node, task_parser=None, xpath=None):
        xpath = xpath or xpath_eval(node)
        documentation_node = first(xpath('.//bpmn:documentation'))
        return self.parse_documentation(documentation_node, node, xpath, task_parser=task_parser)

    def parse_documentation(self, documentation_node, node, node_xpath, task_parser=None):
        """
        Pre-parse the documentation node for the given node and return the text.
        """
        return None if documentation_node is None else documentation_node.text

    def get_spec(self, process_id_or_name):
        """
        Parses the required subset of the BPMN files, in order to provide an instance of BpmnProcessSpec (i.e. WorkflowSpec)
        for the given process ID or name. The Name is matched first.
        """
        return self.get_process_parser(process_id_or_name).get_spec()
