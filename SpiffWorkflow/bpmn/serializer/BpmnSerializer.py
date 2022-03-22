# -*- coding: utf-8 -*-
# Copyright (C) 2020 Matthew Hampton, Dan Funk
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
from lxml import etree
import zipfile
import os
from json import loads

from ...bpmn.specs.SubWorkflowTask import SubWorkflowTask
from ...bpmn.workflow import BpmnWorkflow
from ...serializer import json as spiff_json
from ..parser.BpmnParser import BpmnParser
from .Packager import Packager


class BpmnSerializer(spiff_json.JSONSerializer):
    """
    The BpmnSerializer class provides support for deserializing a Bpmn Workflow
    Spec from a BPMN package. The BPMN package must have been created using the
    :class:`SpiffWorkflow.bpmn.serializer.Packager`.

    It will also use the appropriate subclass of BpmnParser, if one is included
    in the metadata.ini file.

    """

    def serialize_workflow(self, workflow, **kwargs):
        """
        Serializes the workflow data and task tree.  Will also serialize
        the Spec if 'include_spec' kwarg is not set to false.
        """
        assert isinstance(workflow, BpmnWorkflow)
        include_spec = kwargs.get('include_spec',True)
        return super().serialize_workflow(workflow, include_spec=include_spec)

    def serialize_task(self, task, skip_children=False, **kwargs):
        return super().serialize_task(task,
                                      skip_children=skip_children,
                                      allow_subs=True)

    def deserialize_workflow(self, s_state,  workflow_spec=None,
                             read_only=False, **kwargs):

        return super().deserialize_workflow(s_state,
                                            wf_class=BpmnWorkflow,
                                            wf_spec=workflow_spec,
                                            read_only=read_only,
                                            **kwargs)

    def _deserialize_task_children(self, task, s_state):
        """Reverses the internal process that will merge children from a
        sub-workflow in the top level workflow.  This copies the states
        back into the sub-workflow after generating it from the base spec"""
        if not isinstance(task.task_spec, SubWorkflowTask):
            return super()._deserialize_task_children(task, s_state)
        else:
            sub_workflow = task.task_spec.create_sub_workflow(task)
            children = []
            for c in s_state['children']:
                # One child belongs to the parent workflow (The path back
                # out of the subworkflow) the other children belong to the
                # sub-workflow.

                # We need to determine if we are still in the same workflow,
                # Ideally we can just check:  if c['workflow_name'] == sub_workflow.name
                # however, we need to support deserialization of workflows without this
                # critical property, at least temporarily, so people can migrate.
                if 'workflow_name' in c:
                    same_workflow = c['workflow_name'] == sub_workflow.name
                else:
                    same_workflow = sub_workflow.get_tasks_from_spec_name(c['task_spec'])

                if same_workflow:
                    start_task = self.deserialize_task(sub_workflow, c)
                    children.append(start_task)
                    start_task.parent = task.id
                    sub_workflow.task_tree = start_task
                    # get a list of tasks in reverse order of change
                    # our last task should be on the top.
                    tasks = sub_workflow.get_tasks(task.COMPLETED)
                    tasks.sort(key=lambda x: x.last_state_change,reverse=True)
                    if len(tasks)>0:
                        last_task = tasks[0]
                        sub_workflow.last_task = last_task
                else:
                    resume_task = self.deserialize_task(task.workflow, c)
                    resume_task.parent = task.id
                    children.append(resume_task)
            return children

    def deserialize_task(self, workflow, s_state):
        assert isinstance(workflow, BpmnWorkflow)
        return super().deserialize_task(workflow, s_state)

    def deserialize_workflow_spec(self, s_state, filename=None):
        """
        :param s_state: a byte-string with the contents of the packaged
        workflow archive, or a file-like object.

        :param filename: the name of the package file.
        """
        if isinstance(s_state,dict):
            return super().deserialize_workflow_spec(s_state)
        if isinstance(s_state,str):
            return super().deserialize_workflow_spec(s_state)
        if isinstance(s_state, bytes):
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
        parser_class_module = config.get(
            'MetaData', 'parser_class_module', fallback=None)

        if parser_class_module:
            mod = __import__(parser_class_module, fromlist=[
                             config.get('MetaData', 'parser_class')])
            parser_class = getattr(mod, config.get('MetaData', 'parser_class'))

        parser = parser_class()

        for info in package_zip.infolist():
            parts = os.path.split(info.filename)
            if (len(parts) == 2 and
                    not parts[0] and parts[1].lower().endswith('.bpmn')):
                # It is in the root of the ZIP and is a BPMN file
                try:
                    svg = package_zip.read(info.filename[:-5] + '.svg')
                except KeyError:
                    svg = None

                bpmn_fp = package_zip.open(info)
                try:
                    bpmn = etree.parse(bpmn_fp)
                finally:
                    bpmn_fp.close()

                parser.add_bpmn_xml(
                    bpmn, svg=svg,
                    filename='%s:%s' % (filename, info.filename))
        spec_name = config.get('MetaData', 'entry_point_process')
        return parser.get_spec(spec_name)
