import unittest
import datetime
import time

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class TimerDateTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.script_engine = PythonScriptEngine(environment=TaskDataEnvironment({
            "datetime": datetime.datetime,
            "timedelta": datetime.timedelta,
        }))
        self.spec, self.subprocesses = self.load_workflow_spec('timer-date-start.bpmn', 'date_timer')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses, script_engine=self.script_engine)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):
        self.workflow.do_engine_steps()
        self.assertEqual(len(self.workflow.waiting_events()), 1)
        loopcount = 0
        starttime = datetime.datetime.now()
        # test bpmn has a timeout of .05s; we should terminate loop before that.
        while len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)) > 0 and loopcount < 8:
            if save_restore:
                self.save_restore()
                self.workflow.script_engine = self.script_engine
            time.sleep(0.01)
            self.workflow.refresh_waiting_tasks()
            loopcount += 1
        endtime = datetime.datetime.now()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertTrue((endtime-starttime) > datetime.timedelta(seconds=.02))