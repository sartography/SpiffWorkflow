# -*- coding: utf-8 -*-
import unittest

from SpiffWorkflow.exceptions import WorkflowTaskException
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'McDonald, danfunk'

def my_custom_function(txt):
    return str(txt).upper()

class CustomBpmnScriptEngine(PythonScriptEngine):
    """This is a custom script processor that can be easily injected into Spiff Workflow.
    It will execute python code read in from the bpmn.  It will also make any scripts in the
     scripts directory available for execution. """
    def __init__(self):
        environment = TaskDataEnvironment({'custom_function': my_custom_function})
        super().__init__(environment=environment)


class CustomInlineScriptTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('custom_function_test*', 'top_workflow')
        script_engine = CustomBpmnScriptEngine()
        self.workflow = BpmnWorkflow(spec, subprocesses, script_engine=script_engine)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testRunThroughSaveRestore(self):
        self.actual_test(save_restore=False)

    def actual_test(self, save_restore):
        if save_restore: self.save_restore()
        self.workflow.do_engine_steps()
        self.complete_subworkflow()
        self.complete_subworkflow()
        if save_restore: self.save_restore()
        data = self.workflow.last_task.data
        self.assertEqual(data['c1'], 'HELLO')
        self.assertEqual(data['c2'], 'GOODBYE')
        self.assertEqual(data['c3'], 'ARRIVEDERCI')

    def test_overwrite_function_with_local_variable(self):
        ready_task = self.workflow.get_tasks(TaskState.READY)[0]
        ready_task.data = {'custom_function': "bill"}
        with self.assertRaises(WorkflowTaskException) as e:
            self.workflow.do_engine_steps()
        self.assertTrue('' in str(e.exception))
        self.assertTrue('custom_function' in str(e.exception))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CustomInlineScriptTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
