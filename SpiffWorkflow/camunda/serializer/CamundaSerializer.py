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

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.serializer import json as spiffJson
from SpiffWorkflow.serializer.json import JSONSerializer

from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.serializer.base import Serializer


class NoBpmnFilesFound(Exception):
    """ The path provided did not contain any BPMN files. """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass


class CamundaSerializer(JSONSerializer):

    """
    The BpmnSerializer class provides support for deserializing a Camunda BPMN file.
    It will also use the Camunda BpmnParser.
    """

    def serialize_workflow_spec(self, wf_spec, **kwargs):
        raise NotImplementedError(
            "The BpmnSerializer class cannot be used to serialize. BPMN "
            "authoring should be done using a supported editor.")

    def serialize_workflow(self, workflow, **kwargs):
        """
        Serializes the workflow data and task tree, but not the specification
        That must be passed in when deserializing the data structure.
        """
        assert isinstance(workflow, BpmnWorkflow)
        s_state = dict()

        # s_state['wf_spec'] = workflow_spec

        # data
        s_state['data'] = self.serialize_dict(workflow.data)

        # last_node
        value = workflow.last_task
        s_state['last_task'] = value.id if value is not None else None

        # outer_workflow
        # s_state['outer_workflow'] = workflow.outer_workflow.id

        # success
        s_state['success'] = workflow.success

        # task_tree
        s_state['task_tree'] = self.serialize_task(workflow.task_tree)

        return spiffJson.dumps(s_state)


    def deserialize_workflow(self, s_state,  **kwargs):
        """Requires that a deserialized version of the workflow spec
        be provided as a named argument."""

        wf_spec = kwargs['wf_spec']
        workflow = BpmnWorkflow(wf_spec)

        dict = spiffJson.loads(s_state)

        # data
        workflow.data = self.deserialize_dict(dict['data'])

        # outer_workflow
        # workflow.outer_workflow =
        # find_workflow_by_id(remap_workflow_id(s_state['outer_workflow']))

        # success
        workflow.success = dict['success']

        # workflow
        workflow.spec = wf_spec

        # task_tree
        workflow.task_tree = self.deserialize_task(
            workflow, dict['task_tree'])

        # Re-connect parents
        for task in workflow.get_tasks():
            task.parent = workflow.get_task(task.parent)

        # last_task
        workflow.last_task = workflow.get_task(dict['last_task'])

        return workflow

    def deserialize_workflow_spec(self, s_state):
        """
        :param s_state: a directory where the BPMN file(s) and images resides, or
        an array of
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
