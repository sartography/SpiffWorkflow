# -*- coding: utf-8 -*-

import sys
import os
import unittest

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'danfunk'


class PythonScriptEngineTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.expressionEngine = PythonScriptEngine()

        # All this, just so we have a task object, not using anything in the Script.
        spec, subprocesses = self.load_workflow_spec('ScriptTest.bpmn', 'ScriptTest')
        workflow = BpmnWorkflow(spec, subprocesses)
        workflow.do_engine_steps()
        self.task = workflow.last_task

    def testFunctionsAndGlobalsAreRemoved(self):
        self.assertIn('testvar', self.task.data)
        self.assertIn('testvar2', self.task.data)
        self.assertIn('sample', self.task.data)
        self.assertNotIn('my_function', self.task.data)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(PythonScriptEngineTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
