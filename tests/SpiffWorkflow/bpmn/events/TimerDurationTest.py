import unittest
import time
from datetime import datetime, timedelta
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class TimerDurationTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.script_engine = PythonScriptEngine(environment=TaskDataEnvironment({"timedelta": timedelta}))
        self.spec, self.subprocesses = self.load_workflow_spec('timer.bpmn', 'timer')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses, script_engine=self.script_engine)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):
        self.workflow.do_engine_steps()
        self.assertEqual(len(self.workflow.waiting_events()), 1)

        loopcount = 0
        starttime = datetime.now()
        # test bpmn has a timeout of .25s; we should terminate loop before that.
        while len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)) > 0 and loopcount < 10:
            if save_restore:
                self.save_restore()
                self.workflow.script_engine = self.script_engine
            time.sleep(0.1)
            self.workflow.refresh_waiting_tasks()
            loopcount += 1
        endtime = datetime.now()
        duration = endtime - starttime
        self.assertEqual(duration < timedelta(seconds=.5), True)
        self.assertEqual(duration > timedelta(seconds=.2), True)
        self.assertEqual(len(self.workflow.waiting_events()), 0)
