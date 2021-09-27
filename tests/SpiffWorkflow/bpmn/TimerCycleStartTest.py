# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
import datetime
import time

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'

counter = 0
def my_custom_function():
    global counter
    counter = counter+1
    return counter

class CustomScriptEngine(PythonScriptEngine):
    """This is a custom script processor that can be easily injected into Spiff Workflow.
    It will execute python code read in from the bpmn.  It will also make any scripts in the
     scripts directory available for execution. """


    def execute(self, task, script, data):
        augmentMethods = {'custom_function': my_custom_function}
        super().execute(task, script, data, external_methods=augmentMethods)
    def eval(self, exp, data):
        return super()._eval(exp, {}, **data)


class TimerCycleStartTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('timer-cycle-start.bpmn', 'timer')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)


    def actual_test(self,save_restore = False):
        global counter
        self.workflow = BpmnWorkflow(self.spec,script_engine=CustomScriptEngine())
        ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEqual(1, len(ready_tasks)) # Start Event
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()
        #ready_tasks = self.workflow.get_tasks(Task.READY)
        #self.assertEqual(1, len(ready_tasks)) # GetCoffee
        # the data doesn't really propagate to the end as in a 'normal' workflow, so I call a
        # custom function that records the number of times this got called so that
        # we can keep track of how many times the triggered item gets called.

        loopcount = 0
        # test bpmn has a timeout of .25s
        # we should terminate loop before that.
        starttime = datetime.datetime.now()
        counter = 0
        while loopcount < 10:
            if len(self.workflow.get_tasks(Task.READY)) >= 2:
                break
            if save_restore:
                self.save_restore()
                self.workflow.script_engine = CustomScriptEngine()
            waiting_tasks = self.workflow.get_tasks(Task.WAITING)
            #self.assertEqual(1, len(waiting_tasks))
            time.sleep(0.1)
            self.workflow.refresh_waiting_tasks()
            loopcount = loopcount +1
        endtime = datetime.datetime.now()
        self.assertEqual(counter,2)



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TimerCycleStartTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
