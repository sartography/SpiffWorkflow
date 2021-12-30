# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest

from SpiffWorkflow import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class SignalTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('signal.bpmn','signal')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        task = self.workflow.get_tasks(Task.READY)[0]
        self.assertEqual('wait_here', task.get_name())
        self.workflow.signal('cancel')
        self.assertTrue(self.workflow.is_completed())
        self.assertTrue(self.workflow.last_task.data['signal_caught'])

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SignalTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
