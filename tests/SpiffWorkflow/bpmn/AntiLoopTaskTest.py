# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.exceptions import WorkflowException
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class AntiLoopTaskTest(BpmnWorkflowTestCase):
    """The example bpmn is actually a MultiInstance. It should not report that it is a looping task and 
       it should fail when we try to terminate the loop"""

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('bpmnAntiLoopTask.bpmn','LoopTaskTest')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertTrue(len(ready_tasks) ==1)
        self.assertFalse(ready_tasks[0].task_spec.is_loop_task())
        try:
            ready_tasks[0].terminate_loop()
            self.fail("Terminate Loop should throw and error when called on a non-loop MultiInstance")
        except WorkflowException as ex:
            self.assertTrue(
            'The method terminate_loop should only be called in the case of a BPMN Loop Task' in (
                    '%r' % ex),
                           '\'The method terminate_loop should only be called in the case of a BPMN Loop Task\' should be a substring of error message: \'%r\'' % ex)




def suite():
    return unittest.TestLoader().loadTestsFromTestCase(AntiLoopTaskTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
