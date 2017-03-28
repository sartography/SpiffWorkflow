# -*- coding: utf-8 -*-
from __future__ import division, absolute_import
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

import configparser
from io import BytesIO, TextIOWrapper
import xml.etree.ElementTree as ET
import zipfile
import os
from ...serializer.base import Serializer
from ..parser.BpmnParser import BpmnParser
from .Packager import Packager


class BpmnSerializer(Serializer):

    """
    The BpmnSerializer class provides support for deserializing a Bpmn Workflow Spec from a BPMN package.
    The BPMN package must have been created using the :class:`SpiffWorkflow.bpmn.serializer.Packager`.

    It will also use the appropriate subclass of BpmnParser, if one is included in the metadata.ini file.
    """

    def serialize_workflow_spec(self, wf_spec, **kwargs):
        raise NotImplementedError(
            "The BpmnSerializer class cannot be used to serialize. BPMN authoring should be done using a supported editor.")

    def serialize_workflow(self, workflow, **kwargs):
        raise NotImplementedError(
            "The BPMN standard does not provide a specification for serializing a running workflow.")

    def deserialize_workflow(self, s_state, **kwargs):
        raise NotImplementedError(
            "The BPMN standard does not provide a specification for serializing a running workflow.")

    def deserialize_workflow_spec(self, s_state, filename=None):
        """
        :param s_state: a byte-string with the contents of the packaged workflow archive, or a file-like object.
        :param filename: the name of the package file.
        """
        if isinstance(s_state, (str, bytes)):
            s_state = BytesIO(s_state)

        package_zip = zipfile.ZipFile(
            s_state, "r", compression=zipfile.ZIP_DEFLATED)
        config = configparser.ConfigParser()
        ini_fp = TextIOWrapper(
            package_zip.open(Packager.METADATA_FILE), encoding="UTF-8")
        try:
            config.read_file(ini_fp)
        finally:
            ini_fp.close()

        parser_class = BpmnParser

        try:
            parser_class_module = config.get(
                'MetaData', 'parser_class_module', fallback=None)
        except TypeError:
            # unfortunately the fallback= does not exist on python 2
            parser_class_module = config.get(
                'MetaData', 'parser_class_module', None)

        if parser_class_module:
            mod = __import__(parser_class_module, fromlist=[
                             config.get('MetaData', 'parser_class')])
            parser_class = getattr(mod, config.get('MetaData', 'parser_class'))

        parser = parser_class()

        for info in package_zip.infolist():
            parts = os.path.split(info.filename)
            if len(parts) == 2 and not parts[0] and parts[1].lower().endswith('.bpmn'):
                # It is in the root of the ZIP and is a BPMN file
                try:
                    svg = package_zip.read(info.filename[:-5] + '.svg')
                except KeyError as e:
                    svg = None

                bpmn_fp = package_zip.open(info)
                try:
                    bpmn = ET.parse(bpmn_fp)
                finally:
                    bpmn_fp.close()

                parser.add_bpmn_xml(
                    bpmn, svg=svg, filename='%s:%s' % (filename, info.filename))

        return parser.get_spec(config.get('MetaData', 'entry_point_process'))
