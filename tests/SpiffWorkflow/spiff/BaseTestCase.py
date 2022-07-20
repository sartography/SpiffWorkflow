# -*- coding: utf-8 -*-
import os

from SpiffWorkflow.spiff.parser import SpiffBpmnParser
from SpiffWorkflow.spiff.serializer import (NoneTaskConverter, ManualTaskConverter, UserTaskConverter,
        SubWorkflowTaskConverter, TransactionSubprocessConverter, CallActivityTaskConverter)
from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter([
    NoneTaskConverter, ManualTaskConverter, UserTaskConverter,
    SubWorkflowTaskConverter, TransactionSubprocessConverter, CallActivityTaskConverter
])

class BaseTestCase(BpmnWorkflowTestCase):
    """ Provides some basic tools for loading up and parsing Spiff extensions"""

    serializer = BpmnWorkflowSerializer(wf_spec_converter)

    def load_workflow_spec(self, filename, process_name):
        f = os.path.join(os.path.dirname(__file__), 'data', filename)
        parser = SpiffBpmnParser()
        parser.add_bpmn_files_by_glob(f)
        top_level_spec = parser.get_spec(process_name)
        subprocesses = parser.get_subprocess_specs(process_name)
        return top_level_spec, subprocesses

