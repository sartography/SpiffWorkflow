# -*- coding: utf-8 -*-

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskException
from SpiffWorkflow.task import TaskState

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'danfunk'


class PythonScriptEngineTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.expressionEngine = PythonScriptEngine()
        spec, subprocesses = self.load_workflow_spec('ScriptTest.bpmn', 'Process_1l85e0n')
        self. workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):

        self.workflow.do_engine_steps()
        data = self.workflow.last_task.data
        self.assertEqual(data,{'testvar': {'a': 1, 'b': 2, 'new': 'Test'},
                               'testvar2': [{'x': 1, 'y': 'a'},
                                            {'x': 2, 'y': 'b'},
                                            {'x': 3, 'y': 'c'}],
                               'sample': ['b', 'c']})

    def testNoDataPollution(self):
        """Ran into an issue where data from one run of a workflow could
        bleed into a separate execution.  It will think a variable is there
        when it should not be there"""
        startTask = self.workflow.get_tasks(TaskState.READY)[0]
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertTrue("testvar" in self.workflow.last_task.data)
        self.assertFalse("testvar" in startTask.data)

        # StartTask doesn't know about testvar, it happened earlier.
        # calling an exec that references testvar, in the context of the
        # start task should fail.
        with self.assertRaises(WorkflowTaskException):
            self.workflow.script_engine.evaluate(startTask, 'testvar == True')

    def testFunctionsAndGlobalsAreRemoved(self):
        self.workflow.do_engine_steps()
        task = self.workflow.last_task
        self.assertIn('testvar', task.data)
        self.assertIn('testvar2', task.data)
        self.assertIn('sample', task.data)
        self.assertNotIn('my_function', task.data)
