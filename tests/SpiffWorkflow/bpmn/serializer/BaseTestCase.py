import unittest
import os

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow, BpmnTaskFilter
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
from SpiffWorkflow.task import TaskState


class BaseTestCase(unittest.TestCase):

    SERIALIZER_VERSION = "100.1.ANY"
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

    ready_task_filter = BpmnTaskFilter(state=TaskState.READY)
    waiting_task_filter = BpmnTaskFilter(state=TaskState.WAITING)

    def get_ready_user_tasks(self, lane=None):
        return self.workflow.get_tasks(task_filter=BpmnTaskFilter(state=TaskState.READY, manual=True, lane=lane))

    def get_first_task_from_spec_name(self, wf, spec_name):
        return wf.get_tasks(task_filter=BpmnTaskFilter(spec_name=spec_name))[0]

    def load_workflow_spec(self, filename, process_name):
        parser = BpmnParser()
        parser.add_bpmn_files_by_glob(os.path.join(self.DATA_DIR, filename))
        top_level_spec = parser.get_spec(process_name)
        subprocesses = parser.get_subprocess_specs(process_name)
        return top_level_spec, subprocesses

    def setUp(self):
        super(BaseTestCase, self).setUp()
        wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter()
        self.serializer = BpmnWorkflowSerializer(wf_spec_converter, version=self.SERIALIZER_VERSION)
        spec, subprocesses = self.load_workflow_spec('random_fact.bpmn', 'random_fact')
        self.workflow = BpmnWorkflow(spec, subprocesses)
