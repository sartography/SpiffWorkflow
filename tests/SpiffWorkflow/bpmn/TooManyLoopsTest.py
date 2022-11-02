# -*- coding: utf-8 -*-

import datetime
import unittest

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'sartography'

class CustomScriptEngine(PythonScriptEngine):
    """This is a custom script processor that can be easily injected into Spiff Workflow.
    It will execute python code read in from the bpmn.  It will also make any scripts in the
     scripts directory available for execution. """
    def __init__(self):
        augment_methods = {
            'timedelta': datetime.timedelta,
        }
        super().__init__(scripting_additions=augment_methods)

class TooManyLoopsTest(BpmnWorkflowTestCase):

    """Looping back around many times would cause the tree of tasks to grow
    for each loop, doing this a 100 or 1000 times would cause the system to
    run fail in various ways.  This assures that is no longer the case."""

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):
        spec, subprocesses = self.load_workflow_spec('too_many_loops*.bpmn', 'loops')
        self.workflow = BpmnWorkflow(spec, subprocesses, script_engine=CustomScriptEngine())
        counter = 0
        data = {}
        while not self.workflow.is_completed():
            self.workflow.do_engine_steps()
            self.workflow.refresh_waiting_tasks()
            if (self.workflow.last_task.data != data):
                data = self.workflow.last_task.data
            counter += 1  # There is a 10 millisecond wait task.
            if save_restore:
                self.save_restore()
                self.workflow.script_engine = CustomScriptEngine()
        self.assertEqual(20, self.workflow.last_task.data['counter'])

    def test_with_sub_process(self):
        # Found an issue where looping back would fail when it happens
        # right after a sub-process.  So assuring this is fixed.
        counter = 0
        spec, subprocesses = self.load_workflow_spec('too_many_loops_sub_process.bpmn', 'loops_sub')
        self.workflow = BpmnWorkflow(spec, subprocesses, script_engine=CustomScriptEngine())
        data = {}
        while not self.workflow.is_completed():
            self.workflow.do_engine_steps()
            self.workflow.refresh_waiting_tasks()
            if (self.workflow.last_task.data != data):
                data = self.workflow.last_task.data
            counter += 1  # There is a 10 millisecond wait task.
#            self.save_restore()
        self.assertEqual(20, self.workflow.last_task.data['counter'])
        # One less, because we don't go back through once the first counter
        # hits 20.
        self.assertEqual(19, self.workflow.last_task.data['counter2'])

    def test_with_two_call_activities(self):
        spec, subprocess = self.load_workflow_spec('sub_in_loop*.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec, subprocess, script_engine=CustomScriptEngine())
        self.workflow.do_engine_steps()
        for loop in range(3):
            ready = self.workflow.get_ready_user_tasks()
            ready[0].data = { 'done': True if loop == 3 else False }
            ready[0].complete()
            self.workflow.refresh_waiting_tasks()
            self.workflow.do_engine_steps()
            self.save_restore()
            self.workflow.script_engine = CustomScriptEngine()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TooManyLoopsTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
