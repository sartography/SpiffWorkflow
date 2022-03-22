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

import glob

from lxml import etree

from ..workflow import BpmnWorkflow
from .ValidationException import ValidationException
from ..specs.events import StartEvent, EndEvent, BoundaryEvent, IntermediateCatchEvent, IntermediateThrowEvent
from ..specs.SubWorkflowTask import CallActivity, TransactionSubprocess
from ..specs.ExclusiveGateway import ExclusiveGateway
from ..specs.InclusiveGateway import InclusiveGateway
from ..specs.ManualTask import ManualTask
from ..specs.NoneTask import NoneTask
from ..specs.ParallelGateway import ParallelGateway
from ..specs.ScriptTask import ScriptTask
from ..specs.UserTask import UserTask
from .ProcessParser import ProcessParser
from .util import full_tag, xpath_eval, first
from .task_parsers import (UserTaskParser, NoneTaskParser, ManualTaskParser,
                           ExclusiveGatewayParser, ParallelGatewayParser, InclusiveGatewayParser,
                           CallActivityParser, TransactionSubprocessParser,
                           ScriptTaskParser, SubWorkflowParser)
from .event_parsers import (StartEventParser, EndEventParser, BoundaryEventParser,
                           IntermediateCatchEventParser, IntermediateThrowEventParser)

CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'

class BpmnParser(object):
    """
    The BpmnParser class is a pluggable base class that manages the parsing of
    a set of BPMN files. It is intended that this class will be overriden by an
    application that implements a BPMN engine.

    Extension points: OVERRIDE_PARSER_CLASSES provides a map from full BPMN tag
    name to a TaskParser and Task class. PROCESS_PARSER_CLASS provides a
    subclass of ProcessParser WORKFLOW_CLASS provides a subclass of
    BpmnWorkflow
    """

    PARSER_CLASSES = {
        full_tag('startEvent'): (StartEventParser, StartEvent),
        full_tag('endEvent'): (EndEventParser, EndEvent),
        full_tag('userTask'): (UserTaskParser, UserTask),
        full_tag('task'): (NoneTaskParser, NoneTask),
        full_tag('subProcess'): (SubWorkflowParser, CallActivity),
        full_tag('manualTask'): (ManualTaskParser, ManualTask),
        full_tag('exclusiveGateway'): (ExclusiveGatewayParser,
                                       ExclusiveGateway),
        full_tag('parallelGateway'): (ParallelGatewayParser, ParallelGateway),
        full_tag('inclusiveGateway'): (InclusiveGatewayParser,
                                       InclusiveGateway),
        full_tag('callActivity'): (CallActivityParser, CallActivity),
        full_tag('transaction'): (TransactionSubprocessParser, TransactionSubprocess),
        full_tag('scriptTask'): (ScriptTaskParser, ScriptTask),
        full_tag('intermediateCatchEvent'): (IntermediateCatchEventParser,
                                             IntermediateCatchEvent),
        full_tag('intermediateThrowEvent'): (IntermediateThrowEventParser,
                                             IntermediateThrowEvent),
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
        Returns the ProcessParser for the given process ID or name. It matches
        by name first.
        """
        if process_id_or_name in self.process_parsers_by_name:
            return self.process_parsers_by_name[process_id_or_name]
        elif process_id_or_name in self.process_parsers:
            return self.process_parsers[process_id_or_name]

    def get_process_ids(self):
        """Returns a list of process IDs"""
        return  self.process_parsers.keys()

    def add_bpmn_file(self, filename):
        """
        Add the given BPMN filename to the parser's set.
        """
        self.add_bpmn_files([filename])

    def add_bpmn_files_by_glob(self, g):
        """
        Add all filenames matching the provided pattern (e.g. *.bpmn) to the
        parser's set.
        """
        self.add_bpmn_files(glob.glob(g))

    def add_bpmn_files(self, filenames):
        """
        Add all filenames in the given list to the parser's set.
        """
        for filename in filenames:
            f = open(filename, 'r')
            try:
                self.add_bpmn_xml(etree.parse(f), filename=filename)
            finally:
                f.close()

    def add_bpmn_xml(self, bpmn, svg=None, filename=None):
        """
        Add the given lxml representation of the BPMN file to the parser's set.

        :param svg: Optionally, provide the text data for the SVG of the BPMN
          file
        :param filename: Optionally, provide the source filename.
        """
        xpath = xpath_eval(bpmn)
        # do a check on our bpmn to ensure that no id appears twice
        # this *should* be taken care of by our modeler - so this test
        # should never fail.
        ids = [x for x in xpath('.//bpmn:*[@id]')]
        foundids = {}
        for node in ids:
            id = node.get('id')
            if foundids.get(id,None) is not None:
                raise ValidationException(
                    'The bpmn document should have no repeating ids but (%s) repeats'%id,
                    node=node,
                    filename=filename)
            else:
                foundids[id] = 1

        processes = xpath('.//bpmn:process')
        for process in processes:
            self.add_process(process, xpath, svg, filename)

    def add_process(self, process, doc_xpath, svg=None, filename=None, current_lane=None):
        process_parser = self.PROCESS_PARSER_CLASS(self, process, svg, filename=filename, doc_xpath=doc_xpath,
                                                   current_lane=current_lane)
        if process_parser.get_id() in self.process_parsers:
            raise ValidationException('Duplicate process ID', node=process, filename=filename)
        if process_parser.get_name() in self.process_parsers_by_name:
            raise ValidationException('Duplicate process name', node=process, filename=filename)
        self.process_parsers[process_parser.get_id()] = process_parser
        self.process_parsers_by_name[process_parser.get_name()] = process_parser

    def _parse_condition(self, outgoing_task, outgoing_task_node,
                         sequence_flow_node, task_parser=None):
        xpath = xpath_eval(sequence_flow_node)
        condition_expression_node = conditionExpression = first(
            xpath('.//bpmn:conditionExpression'))
        if conditionExpression is not None:
            conditionExpression = conditionExpression.text
        return self.parse_condition(
            conditionExpression, outgoing_task, outgoing_task_node,
            sequence_flow_node, condition_expression_node, task_parser)

    def parse_condition(self, condition_expression, outgoing_task,
                        outgoing_task_node, sequence_flow_node,
                        condition_expression_node, task_parser):
        """
        Pre-parse the given condition expression, and return the parsed
        version. The returned version will be passed to the Script Engine for
        evaluation.
        """
        return condition_expression

    def parse_extensions(self, node, task_parser=None, xpath=None):
        extensions = {}
        xpath = xpath or xpath_eval(node)
        extension_nodes = xpath(
            './/bpmn:extensionElements/{%s}properties/{%s}property'%(
                CAMUNDA_MODEL_NS,CAMUNDA_MODEL_NS))
        for node in extension_nodes:
            extensions[node.get('name')] = node.get('value')
        return extensions

    def _parse_documentation(self, node, task_parser=None, xpath=None):
        xpath = xpath or xpath_eval(node)
        documentation_node = first(xpath('.//bpmn:documentation'))
        return self.parse_documentation(documentation_node, node, xpath,
                                        task_parser=task_parser)

    def parse_documentation(self, documentation_node, node, node_xpath,
                            task_parser=None):
        """
        Pre-parse the documentation node for the given node and return the
        text.
        """
        return None if documentation_node is None else documentation_node.text

    def get_spec(self, process_id_or_name):
        """
        Parses the required subset of the BPMN files, in order to provide an
        instance of BpmnProcessSpec (i.e. WorkflowSpec)
        for the given process ID or name. The Name is matched first.
        """
        parser = self.get_process_parser(process_id_or_name)
        if parser is None:
            raise Exception(
                f"The process '{process_id_or_name}' was not found. "
                f"Did you mean one of the following: "
                f"{', '.join(self.get_process_ids())}?")
        return parser.get_spec()
