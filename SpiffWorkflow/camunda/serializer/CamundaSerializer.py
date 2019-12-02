# -*- coding: utf-8 -*-
from __future__ import division, absolute_import
# Copyright (C) 2019 Dan Funk
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
import os
import xml.etree.ElementTree as ET
import glob

from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.serializer.base import Serializer


class NoBpmnFilesFound(Exception):
    """ The path provided did not contain any BPMN files. """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass


class CamundaSerializer(Serializer):

    """
    The BpmnSerializer class provides support for deserializing a Camunda BPMN file.
    It will also use the Camunda BpmnParser.
    """

    def serialize_workflow_spec(self, wf_spec, **kwargs):
        raise NotImplementedError(
            "The BpmnSerializer class cannot be used to serialize. BPMN "
            "authoring should be done using a supported editor.")

    def serialize_workflow(self, workflow, **kwargs):
        raise NotImplementedError(
            "The BPMN standard does not provide a specification for serializing a running workflow.")

    def deserialize_workflow(self, s_state, **kwargs):
        raise NotImplementedError(
            "The BPMN standard does not provide a specification for serializing a running workflow.")

    def deserialize_workflow_spec(self, s_state):
        """
        :param s_state: a directory where the BPMN file(s) and images resides.
        """
        parser = CamundaParser()

        bpmn_files = glob.glob(s_state + "/*.bpmn")
        if len(bpmn_files) == 0:
            raise NoBpmnFilesFound("No BPMN files here: " +
                                   os.path.abspath(s_state))
        for filename in bpmn_files:
            print(filename)
            try:
                f = open(filename[:-5] + '.svg', "r")
                svg = f.read()
            except FileNotFoundError as e:
                svg = None

            bpmn_fp = open(filename, "r")
            try:
                bpmn = ET.parse(bpmn_fp)
                process_id = self.__get_process_id(bpmn.getroot())
            finally:
                bpmn_fp.close()

            parser.add_bpmn_xml(bpmn, svg=svg, filename=filename)

        return parser.get_spec(process_id)

    def __get_process_id(self, et_root):
        process_elements = []
        for child in et_root:
            if child.tag.endswith('process') and child.attrib.get('isExecutable', False):
                process_elements.append(child)

        if len(process_elements) == 0:
            raise Exception('No executable process tag found')

        if len(process_elements) > 1:
            raise Exception('Multiple executable processes tags found')

        return process_elements[0].attrib['id']
