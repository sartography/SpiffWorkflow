# -*- coding: utf-8 -*-
import os

from SpiffWorkflow.spiff.parser import SpiffBpmnParser
from SpiffWorkflow.spiff.serializer import NoneTaskConverter, \
    ManualTaskConverter, UserTaskConverter, \
    SubWorkflowTaskConverter, TransactionSubprocessConverter, \
    CallActivityTaskConverter, \
    StartEventConverter, EndEventConverter, BoundaryEventConverter, \
    SendTaskConverter, ReceiveTaskConverter, \
    IntermediateCatchEventConverter, IntermediateThrowEventConverter, \
    ServiceTaskConverter
from SpiffWorkflow.dmn.serializer.task_spec_converters import BusinessRuleTaskConverter
from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter([
    NoneTaskConverter, ManualTaskConverter, UserTaskConverter,
    SubWorkflowTaskConverter, TransactionSubprocessConverter, CallActivityTaskConverter,
    StartEventConverter, EndEventConverter, BoundaryEventConverter, SendTaskConverter, ReceiveTaskConverter,
    IntermediateCatchEventConverter, IntermediateThrowEventConverter, BusinessRuleTaskConverter,
    ServiceTaskConverter
])

class BaseTestCase(BpmnWorkflowTestCase):
    """ Provides some basic tools for loading up and parsing Spiff extensions"""

    serializer = BpmnWorkflowSerializer(wf_spec_converter)

    def load_workflow_spec(self, filename, process_name, dmn_filename=None):
        bpmn = os.path.join(os.path.dirname(__file__), 'data', filename)
        parser = SpiffBpmnParser()
        parser.add_bpmn_files_by_glob(bpmn)
        if dmn_filename is not None:
            dmn = os.path.join(os.path.dirname(__file__), 'data', 'dmn', dmn_filename)
            parser.add_dmn_files_by_glob(dmn)
        top_level_spec = parser.get_spec(process_name)
        subprocesses = parser.get_subprocess_specs(process_name)
        return top_level_spec, subprocesses

    def load_collaboration(self, filename, collaboration_name):
        f = os.path.join(os.path.dirname(__file__), 'data', filename)
        parser = SpiffBpmnParser()
        parser.add_bpmn_files_by_glob(f)
        return parser.get_collaboration(collaboration_name)

    def get_all_specs(self, filename):
        f = os.path.join(os.path.dirname(__file__), 'data', filename)
        parser = SpiffBpmnParser()
        parser.add_bpmn_files_by_glob(f)
        return parser.find_all_specs()
