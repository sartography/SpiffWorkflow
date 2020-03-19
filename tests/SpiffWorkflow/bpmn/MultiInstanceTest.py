# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class MultiInstanceTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('bpmnMultiUserTask.bpmn','MultiInstance')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.do_next_exclusive_step('Activity_Loop')
        self.do_next_exclusive_step('Activity_Loop')
        self.do_next_exclusive_step('Activity_Loop')
        self.do_next_exclusive_step('Activity_Loop')
        self.do_next_exclusive_step('Activity_Loop')




    def testSaveRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.do_next_exclusive_step('Activity_Loop')
        self.do_next_exclusive_step('Activity_Loop')
        self.save_restore()
        self.do_next_exclusive_step('Activity_Loop')
        self.do_next_exclusive_step('Activity_Loop')
        self.save_restore()      
        self.do_next_exclusive_step('Activity_Loop')


        


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MultiInstanceTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
