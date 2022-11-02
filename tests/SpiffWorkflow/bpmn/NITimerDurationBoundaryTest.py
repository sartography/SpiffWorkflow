# -*- coding: utf-8 -*-

import unittest
import datetime
import time
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class NITimerDurationTest(BpmnWorkflowTestCase):
    """
    Non-Interrupting Timer boundary test
    """
    def setUp(self):
        self.script_engine = PythonScriptEngine(default_globals={"timedelta": datetime.timedelta})
        spec, subprocesses = self.load_workflow_spec('timer-non-interrupt-boundary.bpmn', 'NonInterruptTimer')
        self.workflow = BpmnWorkflow(spec, subprocesses, script_engine=self.script_engine)

    def load_spec(self):
        return

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):

        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(1, len(ready_tasks))
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(1, len(ready_tasks))
        ready_tasks[0].data['work_done'] = 'No'
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()

        loopcount = 0
        # test bpmn has a timeout of .25s
        # we should terminate loop before that.
        starttime = datetime.datetime.now()
        while loopcount < 10:
            ready_tasks = self.workflow.get_tasks(TaskState.READY)
            if len(ready_tasks) > 1:
                break
            if save_restore:
                self.save_restore()
                self.workflow.script_engine = self.script_engine
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
        self.assertEqual(duration<datetime.timedelta(seconds=.5),True)
        self.assertEqual(duration>datetime.timedelta(seconds=.2),True)
        for task in ready_tasks:
            if task.task_spec == 'GetReason':
                task.data['delay_reason'] = 'Just Because'
            else:
                task.data['work_done'] = 'Yes'
            self.workflow.complete_task_from_id(task.id)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(1, len(ready_tasks))
        ready_tasks[0].data['experience'] = 'Great!'
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()
        self.assertEqual(self.workflow.is_completed(),True)
        self.assertEqual(self.workflow.last_task.data,{'work_done': 'Yes', 'experience': 'Great!'})
        print (self.workflow.last_task.data)
        print(duration)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NITimerDurationTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
