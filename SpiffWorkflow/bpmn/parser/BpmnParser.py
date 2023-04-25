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
import os

from lxml import etree
from lxml.etree import LxmlError

from SpiffWorkflow.bpmn.specs.events.event_definitions import NoneEventDefinition

from .ValidationException import ValidationException
from ..specs.BpmnProcessSpec import BpmnProcessSpec
from ..specs.events.EndEvent import EndEvent
from ..specs.events.StartEvent import StartEvent
from ..specs.events.IntermediateEvent import BoundaryEvent, IntermediateCatchEvent, IntermediateThrowEvent, EventBasedGateway
from ..specs.events.IntermediateEvent import SendTask, ReceiveTask
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
from .node_parser import DEFAULT_NSMAP
from .util import full_tag, xpath_eval, first
from .TaskParser import TaskParser
from .task_parsers import (
    GatewayParser,
    ConditionalGatewayParser,
    CallActivityParser,
    ScriptTaskParser,
    SubWorkflowParser,
)
from .event_parsers import (
    EventBasedGatewayParser,
    StartEventParser, EndEventParser,
    BoundaryEventParser,
    IntermediateCatchEventParser,
    IntermediateThrowEventParser,
    SendTaskParser,
    ReceiveTaskParser
)


XSD_PATH = os.path.join(os.path.dirname(__file__), 'schema', 'BPMN20.xsd')

class BpmnValidator:

    def __init__(self, xsd_path=XSD_PATH, imports=None):
        with open(xsd_path) as xsd:
            schema = etree.parse(xsd)
        if imports is not None:
            for ns, fn in imports.items():
                elem = etree.Element(
                    '{http://www.w3.org/2001/XMLSchema}import',
                    namespace=ns,
                    schemaLocation=fn
                )
                schema.getroot().insert(0, elem)
        self.validator = etree.XMLSchema(schema)

    def validate(self, bpmn, filename=None):
        try:
            self.validator.assertValid(bpmn)
        except ValidationException as ve:
            ve.file_name = filename
            ve.line_number = self.validator.error_log.last_error.line
        except LxmlError as le:
            last_error = self.validator.error_log.last_error
            raise ValidationException(last_error.message, file_name=filename,
                                      line_number=last_error.line)

class BpmnParser(object):
    """
    The BpmnParser class is a pluggable base class that manages the parsing of
    a set of BPMN files. It is intended that this class will be overriden by an
    application that implements a BPMN engine.

    Extension points: OVERRIDE_PARSER_CLASSES provides a map from full BPMN tag
    name to a TaskParser and Task class. PROCESS_PARSER_CLASS provides a
    subclass of ProcessParser. DATA_STORE_CLASSES provides a mapping of names to
    subclasses of BpmnDataStoreSpecification that provide a data store
    implementation.
    """

    PARSER_CLASSES = {
        full_tag('startEvent'): (StartEventParser, StartEvent),
        full_tag('endEvent'): (EndEventParser, EndEvent),
        full_tag('userTask'): (TaskParser, UserTask),
        full_tag('task'): (TaskParser, NoneTask),
        full_tag('subProcess'): (SubWorkflowParser, SubWorkflowTask),
        full_tag('manualTask'): (TaskParser, ManualTask),
        full_tag('exclusiveGateway'): (ConditionalGatewayParser, ExclusiveGateway),
        full_tag('parallelGateway'): (GatewayParser, ParallelGateway),
        full_tag('inclusiveGateway'): (ConditionalGatewayParser, InclusiveGateway),
        full_tag('callActivity'): (CallActivityParser, CallActivity),
        full_tag('transaction'): (SubWorkflowParser, TransactionSubprocess),
        full_tag('scriptTask'): (ScriptTaskParser, ScriptTask),
        full_tag('serviceTask'): (TaskParser, ServiceTask),
        full_tag('intermediateCatchEvent'): (IntermediateCatchEventParser, IntermediateCatchEvent),
        full_tag('intermediateThrowEvent'): (IntermediateThrowEventParser, IntermediateThrowEvent),
        full_tag('boundaryEvent'): (BoundaryEventParser, BoundaryEvent),
        full_tag('receiveTask'): (ReceiveTaskParser, ReceiveTask),
        full_tag('sendTask'): (SendTaskParser, SendTask),
        full_tag('eventBasedGateway'): (EventBasedGatewayParser, EventBasedGateway),
    }

    OVERRIDE_PARSER_CLASSES = {}

    PROCESS_PARSER_CLASS = ProcessParser

    DATA_STORE_CLASSES = {}

    def __init__(self, namespaces=None, validator=None):
        """
        Constructor.
        """
        self.namespaces = namespaces or DEFAULT_NSMAP
        self.validator = validator
        self.process_parsers = {}
        self.process_parsers_by_name = {}
        self.collaborations = {}
        self.process_dependencies = set()
        self.messages = {}
        self.correlations = {}
        self.data_stores = {}

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
            with open(filename, 'r') as f:
                self.add_bpmn_file_like_object(f)

    def add_bpmn_file_like_object(self, file_like_object, filename=None):
        """
        Add the given BPMN file like object to the parser's set. 
        """
        self.add_bpmn_xml(etree.parse(file_like_object), filename)

    def add_bpmn_str(self, bpmn_str, filename=None):
        """
        Add the given BPMN string to the parser's set. 
        """
        self.add_bpmn_xml(etree.fromstring(bpmn_str), filename)

    def add_bpmn_xml(self, bpmn, filename=None):
        """
        Add the given lxml representation of the BPMN file to the parser's set.

        :param svg: Optionally, provide the text data for the SVG of the BPMN
          file
        :param filename: Optionally, provide the source filename.
        """
        if self.validator:
            self.validator.validate(bpmn, filename)

        # we need to parse the data stores before _add_process since it creates
        # the parser instances, which need to know about the data stores to
        # resolve data references.
        self._add_data_stores(bpmn)

        self._add_processes(bpmn, filename)
        self._add_collaborations(bpmn)
        self._add_messages(bpmn)
        self._add_correlations(bpmn)

    def _add_processes(self, bpmn, filename=None):
        for process in bpmn.xpath('.//bpmn:process', namespaces=self.namespaces):
            self._find_dependencies(process)
            self.create_parser(process, filename)

    def _add_collaborations(self, bpmn):
        collaboration = first(bpmn.xpath('.//bpmn:collaboration', namespaces=self.namespaces))
        if collaboration is not None:
            collaboration_xpath = xpath_eval(collaboration)
            name = collaboration.get('id')
            self.collaborations[name] = [ participant.get('processRef') for participant in collaboration_xpath('.//bpmn:participant') ]

    def _add_messages(self, bpmn):
        for message in bpmn.xpath('.//bpmn:message', namespaces=self.namespaces):
            if message.attrib.get("id") is None:
                raise ValidationException(
                    "Message identifier is missing from bpmn xml"
                )
            self.messages[message.attrib.get("id")] = message.attrib.get("name")

    def _add_correlations(self, bpmn):
        for correlation in bpmn.xpath('.//bpmn:correlationProperty', namespaces=self.namespaces):
            correlation_identifier = correlation.attrib.get("id")
            if correlation_identifier is None:
                raise ValidationException("Correlation identifier is missing from bpmn xml")
            correlation_property_retrieval_expressions = correlation.xpath(
                ".//bpmn:correlationPropertyRetrievalExpression", namespaces = self.namespaces)
            if not correlation_property_retrieval_expressions:
                raise ValidationException(
                    f"Correlation is missing correlation property retrieval expressions: {correlation_identifier}"
                )
            retrieval_expressions = []
            for cpre in correlation_property_retrieval_expressions:
                message_model_identifier = cpre.attrib.get("messageRef")
                if message_model_identifier is None:
                    raise ValidationException(
                        f"Message identifier is missing from correlation property: {correlation_identifier}"
                    )
                children = cpre.getchildren()
                expression = children[0].text if len(children) > 0 else None
                retrieval_expressions.append({"messageRef": message_model_identifier,
                                             "expression": expression})
            self.correlations[correlation_identifier] = {
                "name": correlation.attrib.get("name"),
                "retrieval_expressions": retrieval_expressions
            }

    def _add_data_stores(self, bpmn):
        for data_store in bpmn.xpath('.//bpmn:dataStore', namespaces=self.namespaces):
            data_store_id = data_store.attrib.get("id")
            if data_store_id is None:
                raise ValidationException(
                    "Data Store identifier is missing from bpmn xml"
                )
            data_store_name = data_store.attrib.get("name")
            if data_store_name is None:
                raise ValidationException(
                    "Data Store name is missing from bpmn xml"
                )
            if data_store_name not in self.DATA_STORE_CLASSES:
                raise ValidationException(
                    f"Data Store with name {data_store_name} has no implementation"
                )
            data_store_spec = self.DATA_STORE_CLASSES[data_store_name](
                data_store_id,
                data_store_name,
                data_store.attrib.get('capacity'),
                data_store.attrib.get('isUnlimited'))
            self.data_stores[data_store_id] = data_store_spec

    def _find_dependencies(self, process):
        """Locate all calls to external BPMN, and store their ids in our list of dependencies"""
        for call_activity in process.xpath('.//bpmn:callActivity', namespaces=self.namespaces):
            self.process_dependencies.add(call_activity.get('calledElement'))

    def create_parser(self, node, filename=None, lane=None):
        parser = self.PROCESS_PARSER_CLASS(self, node, self.namespaces, self.data_stores, filename=filename, lane=lane)
        if parser.get_id() in self.process_parsers:
            raise ValidationException(f'Duplicate process ID: {parser.get_id()}', node=node, file_name=filename)
        if parser.get_name() in self.process_parsers_by_name:
            raise ValidationException(f'Duplicate process name: {parser.get_name()}', node=node, file_name=filename)
        self.process_parsers[parser.get_id()] = parser
        self.process_parsers_by_name[parser.get_name()] = parser

    def get_process_dependencies(self):
        return self.process_dependencies

    def get_spec(self, process_id_or_name, required=True):
        """
        Parses the required subset of the BPMN files, in order to provide an
        instance of BpmnProcessSpec (i.e. WorkflowSpec)
        for the given process ID or name. The Name is matched first.
        """
        parser = self.get_process_parser(process_id_or_name)
        if required and parser is None:
            raise ValidationException(
                f"The process '{process_id_or_name}' was not found. "
                f"Did you mean one of the following: "
                f"{', '.join(self.get_process_ids())}?")
        elif parser is not None:
            return parser.get_spec()

    def get_subprocess_specs(self, name, specs=None, require_call_activity_specs=True):
        used = specs or {}
        wf_spec = self.get_spec(name)
        for task_spec in wf_spec.task_specs.values():
            if isinstance(task_spec, SubWorkflowTask) and task_spec.spec not in used:
                subprocess_spec = self.get_spec(task_spec.spec, required=require_call_activity_specs)
                used[task_spec.spec] = subprocess_spec
                if subprocess_spec is not None:
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
