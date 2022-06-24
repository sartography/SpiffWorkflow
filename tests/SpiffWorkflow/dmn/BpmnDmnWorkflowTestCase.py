import os

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

from SpiffWorkflow.dmn.serializer import BusinessRuleTaskConverter

wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter([BusinessRuleTaskConverter])


class BpmnDmnWorkflowTestCase(BpmnWorkflowTestCase):

    serializer = BpmnWorkflowSerializer(wf_spec_converter)

    def load_workflow_spec(self, filename, process_name):
        f = os.path.join(os.path.dirname(__file__), 'data', filename)
        parser = BpmnDmnParser()
        parser.add_bpmn_files_by_glob(f)
        top_level_spec = parser.get_spec(process_name)
        subprocesses = parser.get_process_specs()
        return top_level_spec, subprocesses