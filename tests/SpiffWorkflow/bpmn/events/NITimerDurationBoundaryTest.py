# -*- coding: utf-8 -*-

import unittest
import datetime
import time
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class NITimerDurationTest(BpmnWorkflowTestCase):
    """
    Non-Interrupting Timer boundary test
    """
    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('timer-non-interrupt-boundary.bpmn', 'NonInterruptTimer')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def load_spec(self):
        return

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):

        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        event = self.workflow.get_tasks_from_spec_name('Event_0jyy8ao')[0]
        self.assertEqual(event.state, TaskState.WAITING)

        loopcount = 0
        starttime = datetime.datetime.now()
        # test bpmn has a timeout of .2s; we should terminate loop before that.
        # The subprocess will also wait
        while len(self.workflow.get_waiting_tasks()) == 2 and loopcount < 10:
            if save_restore:
                self.save_restore()
            time.sleep(0.1)
            ready_tasks = self.workflow.get_tasks(TaskState.READY)
            # There should be one ready task until the boundary event fires
            self.assertEqual(len(self.workflow.get_ready_user_tasks()), 1)
            self.workflow.refresh_waiting_tasks()
            self.workflow.do_engine_steps()
            loopcount += 1
    
        endtime = datetime.datetime.now()
        duration = endtime - starttime
        # appropriate time here is .5 seconds due to the .3 seconds that we loop and then
        self.assertEqual(duration < datetime.timedelta(seconds=.5), True)
        self.assertEqual(duration > datetime.timedelta(seconds=.2), True)
        ready_tasks = self.workflow.get_ready_user_tasks()
        # Now there should be two.
        self.assertEqual(len(ready_tasks), 2)
        for task in ready_tasks:
            if task.task_spec.name == 'GetReason':
                task.data['delay_reason'] = 'Just Because'
            elif task.task_spec.name == 'Activity_Work':
                task.data['work_done'] = 'Yes'
            task.run()
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.workflow.do_engine_steps()
        self.complete_subworkflow()
        self.assertEqual(self.workflow.is_completed(), True)
        self.assertEqual(self.workflow.last_task.data, {'work_done': 'Yes', 'delay_reason': 'Just Because'})


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NITimerDurationTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
