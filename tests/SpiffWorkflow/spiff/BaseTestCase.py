import os

from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer
from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG
from SpiffWorkflow.spiff.parser import SpiffBpmnParser, VALIDATOR

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

registry = BpmnWorkflowSerializer.configure(DEFAULT_CONFIG)

class BaseTestCase(BpmnWorkflowTestCase):
    """ Provides some basic tools for loading up and parsing Spiff extensions"""

    serializer = BpmnWorkflowSerializer(registry)

    def load_workflow_spec(self, filename, process_name, dmn_filename=None, validate=True):
        bpmn = os.path.join(os.path.dirname(__file__), 'data', filename)
        parser = SpiffBpmnParser(validator=VALIDATOR if validate else None)
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
