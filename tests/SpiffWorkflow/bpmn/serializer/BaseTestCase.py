import unittest
import os

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.parser import BpmnParser
from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer


class BaseTestCase(unittest.TestCase):

    SERIALIZER_VERSION = "100.1.ANY"
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

    def get_ready_user_tasks(self, lane=None):
        return self.workflow.get_tasks(state=TaskState.READY, manual=True, lane=lane)

    def load_workflow_spec(self, filename, process_name):
        parser = BpmnParser()
        parser.add_bpmn_files_by_glob(os.path.join(self.DATA_DIR, filename))
        top_level_spec = parser.get_spec(process_name)
        subprocesses = parser.get_subprocess_specs(process_name)
        return top_level_spec, subprocesses

    def deserialize_workflow(self, filename):
        fn = os.path.join(self.DATA_DIR, 'serialization', filename)
        with open(fn) as fh:
            return self.serializer.deserialize_json(fh.read())

    def setUp(self):
        super(BaseTestCase, self).setUp()
        wf_spec_converter = BpmnWorkflowSerializer.configure()
        self.serializer = BpmnWorkflowSerializer(wf_spec_converter, version=self.SERIALIZER_VERSION)
        spec, subprocesses = self.load_workflow_spec('random_fact.bpmn', 'random_fact')
        self.workflow = BpmnWorkflow(spec, subprocesses)
