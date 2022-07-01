# -*- coding: utf-8 -*-
import os

from SpiffWorkflow.spiff.parser import SpiffBpmnParser

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase


class BaseTestCase(BpmnWorkflowTestCase):
    """ Provides some basic tools for loading up and parsing Spiff extensions"""

    def load_workflow_spec(self, filename, process_name):
        f = os.path.join(os.path.dirname(__file__), 'data', filename)
        parser = SpiffBpmnParser()
        parser.add_bpmn_files_by_glob(f)
        top_level_spec = parser.get_spec(process_name)
        subprocesses = parser.get_process_specs()
        return top_level_spec, subprocesses

