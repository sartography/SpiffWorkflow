from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase


class MultipleThrowEventIntermediateCatchTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, subprocesses = self.load_collaboration('multiple-throw.bpmn','top')
        self.workflow = BpmnWorkflow(self.spec, subprocesses)

    def testMultipleThrowEventIntermediateCatch(self):
        self.actual_test()

    def testMultipleThrowEventIntermediateCatchSaveRestore(self):
        self.actual_test(True)

    def actual_test(self, save_restore=False):
        if save_restore:
            self.save_restore()
        self.workflow.do_engine_steps()
        self.assertEqual(len(self.workflow.get_waiting_tasks()), 0)
        self.assertEqual(self.workflow.is_completed(), True)


class MultipleThrowEventStartsEventTest(BpmnWorkflowTestCase):

    def setUp(self):
        specs = self.get_all_specs('multiple-throw-start.bpmn')
        self.spec = specs.pop('initiate')
        self.workflow = BpmnWorkflow(self.spec, specs)

    def testMultipleThrowEventStartEvent(self):
        self.actual_test()

    def testMultipleThrowEventStartEventSaveRestore(self):
        self.actual_test(True)

    def actual_test(self, save_restore=False):
        if save_restore:
            self.save_restore()
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 1)
        ready_tasks[0].run()
        self.workflow.do_engine_steps()
        self.assertEqual(self.workflow.is_completed(), True)