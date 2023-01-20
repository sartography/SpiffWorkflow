import unittest
import os

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
from tests.SpiffWorkflow.bpmn.BpmnLoaderForTests import TestUserTaskConverter


class BaseTestCase(unittest.TestCase):

    SERIALIZER_VERSION = "100.1.ANY"
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

    def load_workflow_spec(self, filename, process_name):
        parser = BpmnParser()
        parser.add_bpmn_files_by_glob(os.path.join(self.DATA_DIR, filename))
        top_level_spec = parser.get_spec(process_name)
        subprocesses = parser.get_subprocess_specs(process_name)
        return top_level_spec, subprocesses

    def setUp(self):
        super(BaseTestCase, self).setUp()
        wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter([TestUserTaskConverter])
        self.serializer = BpmnWorkflowSerializer(wf_spec_converter, version=self.SERIALIZER_VERSION)
        spec, subprocesses = self.load_workflow_spec('random_fact.bpmn', 'random_fact')
        self.workflow = BpmnWorkflow(spec, subprocesses)
