# -*- coding: utf-8 -*-



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
    def __init__(self):
        augment_methods = {'custom_function': my_custom_function}
        super().__init__(scriptingAdditions=augment_methods)


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

        # the data doesn't really propagate to the end as in a 'normal' workflow, so I call a
        # custom function that records the number of times this got called so that
        # we can keep track of how many times the triggered item gets called.
        counter = 0

        # We have a loop so we can continue to execute waiting tasks when
        # timers expire.  The test workflow has a wait timer that pauses long enough to
        # allow the cycle to complete twice -- otherwise the first iteration through the
        # cycle process causes the remaining tasks to be cancelled.
        for loopcount in range(10):
            if save_restore:
                self.save_restore()
                self.workflow.script_engine = CustomScriptEngine()
            time.sleep(0.1)
            self.workflow.refresh_waiting_tasks()
            self.workflow.do_engine_steps()
        self.assertEqual(counter, 2)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TimerCycleStartTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
