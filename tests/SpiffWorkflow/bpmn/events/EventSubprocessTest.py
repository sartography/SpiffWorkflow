from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

class EventBasedGatewayTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('event-subprocess.bpmn', 'main')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)

    def testEventSubprocess(self):
        self.actual_test()

    def testEventSubprocessSaveRestore(self):
        self.actual_test(True)

    def actual_test(self, save_restore=False):
        self.workflow.do_engine_steps()
        set_data = self.workflow.get_next_task(spec_name='set_data')
        set_data.data.update(v1=True, v2=False)
        set_data.run()
        self.workflow.do_engine_steps()
        task = self.workflow.get_next_task(spec_name='task')
        self.assertEqual(task.state, TaskState.READY)
        self.assertDictEqual(task.data, {'v1': True, 'v2': False})
        task.run()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.completed)

