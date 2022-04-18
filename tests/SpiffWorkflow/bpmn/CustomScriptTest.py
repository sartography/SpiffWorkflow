# -*- coding: utf-8 -*-




import os
import unittest

from SpiffWorkflow import Task
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.exceptions import WorkflowTaskExecException
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'McDonald, danfunk'

def my_custom_function(txt):
    return str(txt).upper()

class CustomBpmnScriptEngine(PythonScriptEngine):
    """This is a custom script processor that can be easily injected into Spiff Workflow.
    It will execute python code read in from the bpmn.  It will also make any scripts in the
     scripts directory available for execution. """
    def __init__(self):
        augment_methods = {'custom_function': my_custom_function}
        super().__init__(scriptingAdditions=augment_methods)


class CustomInlineScriptTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        x = BpmnParser()
        x.add_bpmn_file(os.path.join(os.path.dirname(__file__), 'data', 'custom_function_test.bpmn'))
        x.add_bpmn_file(os.path.join(os.path.dirname(__file__), 'data', 'custom_function_test_call_activity.bpmn'))
        return x.get_spec('top_workflow')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testRunThroughSaveRestore(self):
        self.actual_test(save_restore=False)

    def actual_test(self, save_restore):
        script_engine = CustomBpmnScriptEngine()
        self.workflow = BpmnWorkflow(self.spec,script_engine=script_engine)
        if save_restore: self.save_restore()
        self.workflow.do_engine_steps()
        if save_restore: self.save_restore()
        data = self.workflow.last_task.data
        self.assertEqual(data['c1'], 'HELLO')
        self.assertEqual(data['c2'], 'GOODBYE')
        self.assertEqual(data['c3'], 'ARRIVEDERCI')

    def test_overwrite_function_with_local_variable(self):
        script_engine = CustomBpmnScriptEngine()
        self.workflow = BpmnWorkflow(self.spec,script_engine=script_engine)
        ready_task = self.workflow.get_tasks(Task.READY)[0]
        ready_task.data = {'custom_function': "bill"}
        with self.assertRaises(WorkflowTaskExecException) as e:
            self.workflow.do_engine_steps()
        self.assertTrue('' in str(e.exception))
        self.assertTrue('custom_function' in str(e.exception))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CustomInlineScriptTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
