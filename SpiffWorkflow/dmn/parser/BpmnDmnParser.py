# Copyright (C) 2023 Sartography
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

import glob
import os

from lxml import etree

from ...bpmn.parser.util import full_tag
from ...bpmn.parser.ValidationException import ValidationException

from ...bpmn.parser.BpmnParser import BpmnParser, BpmnValidator
from ...dmn.parser.DMNParser import DMNParser, get_dmn_ns
from ..engine.DMNEngine import DMNEngine

XSD_DIR = os.path.join(os.path.dirname(__file__), 'schema')
SCHEMAS = {
    'http://www.omg.org/spec/DMN/20151101/dmn.xsd': os.path.join(XSD_DIR, 'DMN.xsd'),
    'http://www.omg.org/spec/DMN/20180521/MODEL/': os.path.join(XSD_DIR, 'DMN12.xsd'),
    'https://www.omg.org/spec/DMN/20191111/MODEL/': os.path.join(XSD_DIR, 'DMN13.xsd'),
}


class BpmnDmnParser(BpmnParser):

    def __init__(self, namespaces=None, validator=None, dmn_schemas=None):
        super().__init__(namespaces, validator)
        self.dmn_schemas = dmn_schemas or SCHEMAS
        self.dmn_parsers = {}
        self.dmn_parsers_by_name = {}
        self.dmn_dependencies = set()

    def get_engine(self, decision_ref, node):
        if decision_ref not in self.dmn_parsers:
            options = ', '.join(list(self.dmn_parsers.keys()))
            raise ValidationException(
                'No DMN Diagram available with id "%s", Available DMN ids are: %s' %(decision_ref, options),
                node=node, file_name='')
        dmn_parser = self.dmn_parsers[decision_ref]
        dmn_parser.parse()
        decision = dmn_parser.decision

        return DMNEngine(decision.decisionTables[0])

    def add_dmn_xml(self, node, filename=None):
        """
        Add the given lxml representation of the DMN file to the parser's set.
        """
        nsmap = get_dmn_ns(node)
        # We have to create a dmn validator on the fly, because we support multiple versions
        # If we have a bpmn validator, assume DMN validation should be done as well.
        # I don't like this, but I don't see a better solution.
        schema = self.dmn_schemas.get(nsmap.get('dmn'))
        if self.validator and schema is not None:
            validator = BpmnValidator(schema)
            validator.validate(node, filename)

        dmn_parser = DMNParser(self, node, nsmap, filename=filename)
        self.dmn_parsers[dmn_parser.bpmn_id()] = dmn_parser
        self.dmn_parsers_by_name[dmn_parser.get_name()] = dmn_parser

    def add_dmn_file(self, filename):
        """
        Add the given DMN filename to the parser's set.
        """
        self.add_dmn_files([filename])

    def add_dmn_files_by_glob(self, g):
        """
        Add all filenames matching the provided pattern (e.g. *.bpmn) to the
        parser's set.
        """
        self.add_dmn_files(glob.glob(g))

    def add_dmn_files(self, filenames):
        """
        Add all filenames in the given list to the parser's set.
        """
        for filename in filenames:
            with open(filename, 'r') as f:
                self.add_dmn_io(f, filename=filename)

    def add_dmn_io(self, file_like_object, filename=None):
        """
        Add the given DMN file like object to the parser's set.
        """
        self.add_dmn_xml(etree.parse(file_like_object).getroot(), filename)

    def add_dmn_str(self, dmn_str, filename=None):
        """
        Add the given DMN string to the parser's set.
        """
        self.add_dmn_xml(etree.fromstring(dmn_str), filename)

    def get_dependencies(self):
        return self.process_dependencies.union(self.dmn_dependencies)

    def get_dmn_dependencies(self):
        return self.dmn_dependencies

    def _find_dependencies(self, process):
        super()._find_dependencies(process)
        parser_cls, cls = self._get_parser_class(full_tag('businessRuleTask'))
        for business_rule in process.xpath('.//bpmn:businessRuleTask', namespaces=self.namespaces):
            self.dmn_dependencies.add(parser_cls.get_decision_ref(business_rule))
