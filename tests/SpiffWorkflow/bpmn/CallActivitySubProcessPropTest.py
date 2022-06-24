# -*- coding: utf-8 -*-



import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class CallActivitySubProcessPropTest(BpmnWorkflowTestCase):
    """
    Make sure that workflow.data propagates to the subworkflows
    in a BPMN
    """

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('proptest-*.bpmn', 'TopLevel')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testSaveRestore(self):
        self.actualTest(True)

    def actualTest(self, save_restore=False):
        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()
        self.assertTrue(self.workflow.is_completed())
        self.assertEqual(self.workflow.data['valA'],1)
        self.assertEqual(self.workflow.data['valB'],1)
        self.assertEqual(self.workflow.data['valC'],1)
        self.assertEqual(self.workflow.data['valD'],1)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CallActivitySubProcessPropTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
