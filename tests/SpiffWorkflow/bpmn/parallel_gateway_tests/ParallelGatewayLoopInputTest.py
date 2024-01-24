from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

class ParallelGatewayLoopInputTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocess_specs = self.load_workflow_spec('gateway_loop_input.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec, subprocess_specs)
    
    def test_loop_input(self):

        self.workflow.do_engine_steps()
        ready = self.workflow.get_tasks(state=TaskState.READY)
        self.assertEqual(len(ready), 1)
        ready[0].run()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertDictEqual(self.workflow.data, { 'x': 2})
