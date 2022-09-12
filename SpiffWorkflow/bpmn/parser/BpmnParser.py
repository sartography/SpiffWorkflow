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

import glob

from lxml import etree

from SpiffWorkflow.bpmn.specs.events.event_definitions import NoneEventDefinition

from .ValidationException import ValidationException
from ..specs.BpmnProcessSpec import BpmnProcessSpec
from ..specs.events import StartEvent, EndEvent, BoundaryEvent, IntermediateCatchEvent, IntermediateThrowEvent
from ..specs.events import SendTask, ReceiveTask
from ..specs.SubWorkflowTask import CallActivity, SubWorkflowTask, TransactionSubprocess
from ..specs.ExclusiveGateway import ExclusiveGateway
from ..specs.InclusiveGateway import InclusiveGateway
from ..specs.ManualTask import ManualTask
from ..specs.NoneTask import NoneTask
from ..specs.ParallelGateway import ParallelGateway
from ..specs.ScriptTask import ScriptTask
from ..specs.ServiceTask import ServiceTask
from ..specs.UserTask import UserTask
from .ProcessParser import ProcessParser
from .util import full_tag, xpath_eval, first
from .task_parsers import (UserTaskParser, NoneTaskParser, ManualTaskParser,
                           ExclusiveGatewayParser, ParallelGatewayParser, InclusiveGatewayParser,
                           CallActivityParser, ScriptTaskParser, SubWorkflowParser,
                           ServiceTaskParser)
from .event_parsers import (StartEventParser, EndEventParser, BoundaryEventParser,
                           IntermediateCatchEventParser, IntermediateThrowEventParser,
                           SendTaskParser, ReceiveTaskParser)


class BpmnParser(object):
    """
    The BpmnParser class is a pluggable base class that manages the parsing of
    a set of BPMN files. It is intended that this class will be overriden by an
    application that implements a BPMN engine.

    Extension points: OVERRIDE_PARSER_CLASSES provides a map from full BPMN tag
    name to a TaskParser and Task class. PROCESS_PARSER_CLASS provides a
    subclass of ProcessParser
    """

    PARSER_CLASSES = {
        full_tag('startEvent'): (StartEventParser, StartEvent),
        full_tag('endEvent'): (EndEventParser, EndEvent),
        full_tag('userTask'): (UserTaskParser, UserTask),
        full_tag('task'): (NoneTaskParser, NoneTask),
        full_tag('subProcess'): (SubWorkflowParser, CallActivity),
        full_tag('manualTask'): (ManualTaskParser, ManualTask),
        full_tag('exclusiveGateway'): (ExclusiveGatewayParser, ExclusiveGateway),
        full_tag('parallelGateway'): (ParallelGatewayParser, ParallelGateway),
        full_tag('inclusiveGateway'): (InclusiveGatewayParser, InclusiveGateway),
        full_tag('callActivity'): (CallActivityParser, CallActivity),
        full_tag('transaction'): (SubWorkflowParser, TransactionSubprocess),
        full_tag('scriptTask'): (ScriptTaskParser, ScriptTask),
        full_tag('serviceTask'): (ServiceTaskParser, ServiceTask),
        full_tag('intermediateCatchEvent'): (IntermediateCatchEventParser, IntermediateCatchEvent),
        full_tag('intermediateThrowEvent'): (IntermediateThrowEventParser, IntermediateThrowEvent),
        full_tag('boundaryEvent'): (BoundaryEventParser, BoundaryEvent),
        full_tag('receiveTask'): (ReceiveTaskParser, ReceiveTask),
        full_tag('sendTask'): (SendTaskParser, SendTask),
    }

    OVERRIDE_PARSER_CLASSES = {}

    PROCESS_PARSER_CLASS = ProcessParser

    def __init__(self):
        """
        Constructor.
        """
        self.process_parsers = {}
        self.process_parsers_by_name = {}
        self.collaborations = {}
        self.process_dependencies = set()
        self.dmn_dependencies = set()

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
        return list(self.process_parsers.keys())

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

    def add_bpmn_xml(self, bpmn, filename=None):
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

        for process in xpath('.//bpmn:process'):
            self.create_parser(process, xpath, filename)

        self._find_dependencies(xpath)

        collaboration = first(xpath('.//bpmn:collaboration'))
        if collaboration is not None:
            collaboration_xpath = xpath_eval(collaboration)
            name = collaboration.get('id')
            self.collaborations[name] = [ participant.get('processRef') for participant in collaboration_xpath('.//bpmn:participant') ]

    def _find_dependencies(self, xpath):
        """Locate all calls to external BPMN and DMN files, and store their
        ids in our list of dependencies"""
        for call_activity in xpath('.//bpmn:callActivity'):
            self.process_dependencies.add(call_activity.get('calledElement'))
        parser_cls, cls = self._get_parser_class(full_tag('businessRuleTask'))
        if parser_cls:
            for business_rule in xpath('.//bpmn:businessRuleTask'):
                self.dmn_dependencies.add(parser_cls.get_decision_ref(business_rule))


    def create_parser(self, node, doc_xpath, filename=None, lane=None):
        parser = self.PROCESS_PARSER_CLASS(self, node, filename=filename, doc_xpath=doc_xpath, lane=lane)
        if parser.get_id() in self.process_parsers:
            raise ValidationException('Duplicate process ID', node=node, filename=filename)
        if parser.get_name() in self.process_parsers_by_name:
            raise ValidationException('Duplicate process name', node=node, filename=filename)
        self.process_parsers[parser.get_id()] = parser
        self.process_parsers_by_name[parser.get_name()] = parser

    def get_dependencies(self):
        return self.process_dependencies.union(self.dmn_dependencies)

    def get_process_dependencies(self):
        return self.process_dependencies

    def get_dmn_dependencies(self):
        return self.dmn_dependencies

    def get_spec(self, process_id_or_name):
        """
        Parses the required subset of the BPMN files, in order to provide an
        instance of BpmnProcessSpec (i.e. WorkflowSpec)
        for the given process ID or name. The Name is matched first.
        """
        parser = self.get_process_parser(process_id_or_name)
        if parser is None:
            raise ValidationException(
                f"The process '{process_id_or_name}' was not found. "
                f"Did you mean one of the following: "
                f"{', '.join(self.get_process_ids())}?")
        return parser.get_spec()

    def get_subprocess_specs(self, name, specs=None):
        used = specs or {}
        wf_spec = self.get_spec(name)
        for task_spec in wf_spec.task_specs.values():
            if isinstance(task_spec, SubWorkflowTask) and task_spec.spec not in used:
                used[task_spec.spec] = self.get_spec(task_spec.spec)
                self.get_subprocess_specs(task_spec.spec, used)
        return used

    def find_all_specs(self):
        # This is a little convoluted, but we might add more processes as we generate
        # the dictionary if something refers to another subprocess that we haven't seen.
        processes = dict((id, self.get_spec(id)) for id in self.get_process_ids())
        while processes.keys() != self.process_parsers.keys():
            for process_id in self.process_parsers.keys():
                processes[process_id] = self.get_spec(process_id)
        return processes

    def get_collaboration(self, name):
        self.find_all_specs()
        spec = BpmnProcessSpec(name)
        subprocesses = {}
        start = StartEvent(spec, 'Start Collaboration', NoneEventDefinition())
        spec.start.connect(start)
        end = EndEvent(spec, 'End Collaboration', NoneEventDefinition())
        end.connect(spec.end)
        for process in self.collaborations[name]:
            process_parser = self.get_process_parser(process)
            if process_parser and process_parser.process_executable:
                participant = CallActivity(spec, process, process)
                start.connect(participant)
                participant.connect(end)
                subprocesses[process] = self.get_spec(process)
                subprocesses.update(self.get_subprocess_specs(process))
        return spec, subprocesses
