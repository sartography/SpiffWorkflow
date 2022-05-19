# -*- coding: utf-8 -*-

import unittest
import datetime
import time
import pytz

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class TimerDateTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('timer-date-start.bpmn', 'date_timer')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)


    def actual_test(self,save_restore = False):
        global counter
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(1, len(ready_tasks)) # Start Event
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()

        loopcount = 0
        # test bpmn has a timeout of .25s
        # we should terminate loop before that.
        starttime = datetime.datetime.now()
        counter = 0
        while loopcount < 8:
            if len(self.workflow.get_tasks(TaskState.READY)) >= 1:
                break
            if save_restore:
                self.save_restore()


            waiting_tasks = self.workflow.get_tasks(TaskState.WAITING)
            time.sleep(0.1)
            self.workflow.refresh_waiting_tasks()
            loopcount = loopcount +1
        endtime = datetime.datetime.now()
        self.workflow.do_engine_steps()
        tz = pytz.timezone('US/Eastern')
        testdate = tz.localize(datetime.datetime.strptime('2021-09-01 10:00','%Y-%m-%d %H:%M'))
        self.assertEqual(self.workflow.last_task.data['futuredate2'],testdate)
        self.assertTrue('completed' in self.workflow.last_task.data)
        self.assertTrue(self.workflow.last_task.data['completed'])
        self.assertTrue((endtime-starttime) > datetime.timedelta(seconds=.25))



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TimerDateTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
