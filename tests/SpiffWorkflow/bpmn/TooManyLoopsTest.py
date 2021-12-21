# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'sartography'


class TooManyLoopsTest(BpmnWorkflowTestCase):

    """Looping back around many times would cause the tree of tasks to grow
    for each loop, doing this a 100 or 1000 times would cause the system to
    run fail in various ways.  This assures that is no longer the case."""

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('too_many_loops.bpmn', 'loops')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)


    def actual_test(self,save_restore = False):
        counter = 0
        self.workflow = BpmnWorkflow(self.spec,script_engine=PythonScriptEngine())
        data = {}
        while not self.workflow.is_completed():
            self.workflow.do_engine_steps()
            self.workflow.refresh_waiting_tasks()
            if (self.workflow.last_task.data != data):
                data = self.workflow.last_task.data
            counter += 1  # There is a 10 millisecond wait task.
            if save_restore:
                self.save_restore()
        self.assertEqual(20, self.workflow.last_task.data['counter'])

    def test_with_sub_process(self):
        # Found an issue where looping back would fail when it happens
        # right after a sub-process.  So assuring this is fixed.
        counter = 0
        spec = self.load_workflow_spec('too_many_loops_sub_process.bpmn', 'loops')
        self.workflow = BpmnWorkflow(spec,script_engine=PythonScriptEngine())
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


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TooManyLoopsTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
