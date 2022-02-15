# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'sartography'


class SameNameBugTest(BpmnWorkflowTestCase):

    """Should we bail out with a good error message, when two BPMN diagrams
    that work with each other, have tasks with the same id?!?"""

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('same_id*.bpmn', 'same_id')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):
        self.workflow = BpmnWorkflow(self.spec,script_engine=PythonScriptEngine())
        if save_restore:
            self.save_restore()
        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SameNameBugTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
