import datetime
import unittest
import time

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'

# the data doesn't really propagate to the end as in a 'normal' workflow, so I call a
# custom function that records the number of times this got called so that
# we can keep track of how many times the triggered item gets called.
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
        environment = TaskDataEnvironment({
            'custom_function': my_custom_function,
            'timedelta': datetime.timedelta,
        })
        super().__init__(environment=environment)


class TimerCycleStartTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('timer-cycle-start.bpmn', 'timer')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses, script_engine=CustomScriptEngine())

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):
        global counter
        counter = 0
        # We have a loop so we can continue to execute waiting tasks when
        # timers expire.  The test workflow has a wait timer that pauses long enough to
        # allow the cycle to complete three times before being cancelled by the terminate
        # event (the timer should only run twice, we want to make sure it doesn't keep
        # executing)
        for loopcount in range(6):
            self.workflow.do_engine_steps()
            if save_restore:
                self.save_restore()
            time.sleep(0.1)
            self.workflow.refresh_waiting_tasks()

        self.assertEqual(counter, 2)
        self.assertTrue(self.workflow.is_completed())
