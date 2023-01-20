from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.exceptions import WorkflowException

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

class InclusiveGatewayTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocess = self.load_workflow_spec('inclusive_gateway.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec)
        self.workflow.do_engine_steps()

    def testDefaultConditionOnly(self):
        self.set_data({'v': -1, 'u': -1, 'w': -1})
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertDictEqual(self.workflow.data, {'v': 0, 'u': -1, 'w': -1})

    def testDefaultConditionOnlySaveRestore(self):
        self.set_data({'v': -1, 'u': -1, 'w': -1})
        self.save_restore()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertDictEqual(self.workflow.data, {'v': 0, 'u': -1, 'w': -1})

    def testNoPathFromSecondGateway(self):
        self.set_data({'v': 0, 'u': -1, 'w': -1})
        self.assertRaises(WorkflowException, self.workflow.do_engine_steps)

    def testParallelCondition(self):
        self.set_data({'v': 0, 'u': 1, 'w': 1})
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertDictEqual(self.workflow.data, {'v': 0, 'u': 1, 'w': 1})

    def set_data(self, value):
        task = self.workflow.get_ready_user_tasks()[0]
        task.data = value
        task.complete()
