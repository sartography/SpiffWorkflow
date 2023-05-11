# -*- coding: utf-8 -*-
import os

from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.serializer.config import CAMUNDA_SPEC_CONFIG

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase


__author__ = 'danfunk'

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(CAMUNDA_SPEC_CONFIG)

class BaseTestCase(BpmnWorkflowTestCase):
    """ Provides some basic tools for loading up and parsing camunda BPMN files """

    serializer = BpmnWorkflowSerializer(wf_spec_converter)

    def get_parser(self, filename, dmn_filename=None):
        f = os.path.join(os.path.dirname(__file__), 'data', filename)
        parser = CamundaParser()
        parser.add_bpmn_files_by_glob(f)
        if dmn_filename is not None:
            dmn = os.path.join(os.path.dirname(__file__), 'data', 'dmn', dmn_filename)
            parser.add_dmn_files_by_glob(dmn)
        return parser

    def load_workflow_spec(self, filename, process_name, dmn_filename=None):
        parser = self.get_parser(filename, dmn_filename)
        top_level_spec = parser.get_spec(process_name)
        subprocesses = parser.get_subprocess_specs(process_name)
        return top_level_spec, subprocesses

    def reload_save_restore(self):
        self.save_restore()
