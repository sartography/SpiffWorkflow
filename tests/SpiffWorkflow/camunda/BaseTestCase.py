# -*- coding: utf-8 -*-
import os

from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.serializer import UserTaskConverter

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase


__author__ = 'danfunk'

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter([UserTaskConverter])
class BaseTestCase(BpmnWorkflowTestCase):
    """ Provides some basic tools for loading up and parsing camunda BPMN files """

    serializer = BpmnWorkflowSerializer(wf_spec_converter)

    def load_workflow_spec(self, filename, process_name):
        f = os.path.join(os.path.dirname(__file__), 'data', filename)
        parser = CamundaParser()
        parser.add_bpmn_files_by_glob(f)
        top_level_spec = parser.get_spec(process_name)
        subprocesses = parser.get_subprocess_specs(process_name)
        return top_level_spec, subprocesses

    def reload_save_restore(self):
        self.save_restore()
