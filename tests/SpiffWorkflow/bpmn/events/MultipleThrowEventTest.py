from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase


class MultipleThrowEventTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, subprocesses = self.load_collaboration('multiple-throw.bpmn','top')
        self.workflow = BpmnWorkflow(self.spec, subprocesses)

    def testMultipleThrowEvent(self):
        self.actual_test()

    def testMultipleThrowEventSaveRestore(self):
        self.actual_test(True)

    def actual_test(self, save_restore=False):
        if save_restore:
            self.save_restore()
        self.workflow.do_engine_steps()
        self.assertEqual(len(self.workflow.get_waiting_tasks()), 0)
        self.assertEqual(self.workflow.is_completed(), True)
