import time
from datetime import timedelta

from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine, TaskDataEnvironment

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class TimerDurationTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.script_engine = PythonScriptEngine(environment=TaskDataEnvironment({"timedelta": timedelta}))
        self.spec, self.subprocesses = self.load_workflow_spec('boundary_timer_on_task.bpmn', 'test_timer')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses, script_engine=self.script_engine)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):

        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()
            self.workflow.script_engine = self.script_engine
        time.sleep(1)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()

        # Make sure the timer got called
        self.assertEqual(self.workflow.last_task.data['timer_called'],True)

        # Make sure the task can still be called.
        task = self.get_ready_user_tasks()[0]
        task.run()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.completed)

