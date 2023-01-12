# -*- coding: utf-8 -*-

import unittest
import time
from datetime import datetime, timedelta
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class TimerDurationTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.script_engine = PythonScriptEngine(default_globals={"timedelta": timedelta})
        self.spec, self.subprocesses = self.load_workflow_spec('timer.bpmn', 'timer')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses, script_engine=self.script_engine)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):
        self.workflow.do_engine_steps()

        loopcount = 0
        starttime = datetime.now()
        # test bpmn has a timeout of .25s; we should terminate loop before that.
        while len(self.workflow.get_waiting_tasks()) > 0 and loopcount < 10:
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


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TimerDurationTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
