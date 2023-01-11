# -*- coding: utf-8 -*-

import datetime
import unittest
import time

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.task import TaskState
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
        augment_methods = {
            'custom_function': my_custom_function,
            'timedelta': datetime.timedelta,
        }
        super().__init__(scripting_additions=augment_methods)



class TimerCycleTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('timer-cycle.bpmn', 'timer')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses, script_engine=CustomScriptEngine())

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):
        global counter
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(1, len(ready_tasks)) # GetCoffee

        # See comments in timer cycle test start for more context
        counter = 0
        for loopcount in range(5):
            if save_restore:
                self.save_restore()
                self.workflow.script_engine = CustomScriptEngine()
            time.sleep(0.1)
            self.workflow.refresh_waiting_tasks()
            self.workflow.do_engine_steps()

        # FIX ME (if possible)
        #self.assertEqual(counter, 2)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TimerCycleTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
