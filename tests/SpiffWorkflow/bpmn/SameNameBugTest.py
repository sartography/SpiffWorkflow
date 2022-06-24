# -*- coding: utf-8 -*-

import unittest

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'sartography'


class SameNameBugTest(BpmnWorkflowTestCase):

    """Should we bail out with a good error message, when two BPMN diagrams
    that work with each other, have tasks with the same id?!?"""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('same_id*.bpmn', 'same_id')
        self.workflow = BpmnWorkflow(spec, subprocesses, script_engine=PythonScriptEngine())

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):
        if save_restore:
            self.save_restore()
        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SameNameBugTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
