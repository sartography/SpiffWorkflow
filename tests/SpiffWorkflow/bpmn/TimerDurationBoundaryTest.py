# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
import datetime
import time
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class TimerDurationTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('boundary.bpmn', 'boundary_event')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)


    def actual_test(self,save_restore = False):
        self.workflow = BpmnWorkflow(self.spec)
        ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEqual(1, len(ready_tasks))
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEqual(1, len(ready_tasks))
        ready_tasks[0].data['answer']='No'
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()

        loopcount = 0
        # test bpmn has a timeout of .25s
        # we should terminate loop before that.
        starttime = datetime.datetime.now()
        while loopcount < 10:
            ready_tasks = self.workflow.get_tasks(Task.READY)
            if len(ready_tasks) < 1:
                break
            if save_restore: self.save_restore()
            #self.assertEqual(1, len(self.workflow.get_tasks(Task.WAITING)))
            time.sleep(0.1)
            self.workflow.complete_task_from_id(ready_tasks[0].id)
            self.workflow.refresh_waiting_tasks()
            self.workflow.do_engine_steps()
            loopcount = loopcount +1
        endtime = datetime.datetime.now()
        duration = endtime-starttime
        # appropriate time here is .5 seconds
        # due to the .3 seconds that we loop and then
        # the two conditions that we complete after the timer completes.
        self.assertEqual(duration<datetime.timedelta(seconds=.6),True)
        self.assertEqual(duration>datetime.timedelta(seconds=.25),True)
        print(duration)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TimerDurationTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
