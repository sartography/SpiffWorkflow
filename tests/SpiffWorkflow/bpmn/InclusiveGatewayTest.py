from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskException
from SpiffWorkflow.util.task import TaskState

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
        self.assertRaises(WorkflowTaskException, self.workflow.do_engine_steps)
        task = self.workflow.get_next_task(spec_name='second')
        self.assertEqual(task.state, TaskState.ERROR)

    def testParallelCondition(self):
        self.set_data({'v': 0, 'u': 1, 'w': 1})
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertDictEqual(self.workflow.data, {'v': 0, 'u': 1, 'w': 1})

    def set_data(self, value):
        task = self.get_ready_user_tasks()[0]
        task.data = value
        task.run()
