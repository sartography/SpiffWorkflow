# -*- coding: utf-8 -*-

import unittest

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.exceptions import WorkflowTaskException
from SpiffWorkflow.task import TaskState

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class CallActivityTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('call_activity_*.bpmn', 'Process_8200379')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.workflow.do_engine_steps()

    def testCallActivityHasSameScriptEngine(self):
        self.runCallActivityWithCustomScript()

    def testCallActivityHasSameScriptEngineAfterSaveRestore(self):
        self.runCallActivityWithCustomScript(save_restore=True)

    def runCallActivityWithCustomScript(self, save_restore=False):
        class CustomScriptEngine(PythonScriptEngine):
            pass

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses,
                                     script_engine=CustomScriptEngine())
        self.workflow.do_engine_steps()
        self.complete_subworkflow()
        self.assertTrue(self.workflow.is_completed())
        self.assertIsInstance(self.workflow.script_engine, CustomScriptEngine)

        if save_restore:
            self.save_restore()

        # Get the subworkflow
        sub_task = self.workflow.get_tasks_from_spec_name('Sub_Bpmn_Task')[0]
        sub_workflow = sub_task.workflow
        self.assertNotEqual(sub_workflow, self.workflow)
        self.assertIsInstance(self.workflow.script_engine, CustomScriptEngine)
        self.assertEqual(sub_workflow.script_engine, self.workflow.script_engine)

    def test_call_activity_allows_removal_of_data(self):
        # If a call activity alters the data - removing existing keys, that
        # data should be removed in the final output as well.
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.workflow.do_engine_steps()
        self.complete_subworkflow()
        self.assertTrue(self.workflow.is_completed())
        self.assertNotIn('remove_this_var', self.workflow.last_task.data.keys())

    def test_call_acitivity_errors_include_task_trace(self):
        error_spec = self.subprocesses.get('ErroringBPMN')
        error_spec, subprocesses = self.load_workflow_spec('call_activity_*.bpmn', 'ErroringBPMN')
        with self.assertRaises(WorkflowTaskException) as context:
            self.workflow = BpmnWorkflow(error_spec, subprocesses)
            self.workflow.do_engine_steps()
        self.assertEquals(2, len(context.exception.task_trace))
        self.assertRegexpMatches(context.exception.task_trace[0], 'Create Data \(.*?call_activity_call_activity.bpmn\)')
        self.assertRegexpMatches(context.exception.task_trace[1], 'Get Data Call Activity \(.*?call_activity_with_error.bpmn\)')
        task = self.workflow.get_tasks_from_spec_name('Sub_Bpmn_Task')[0]
        self.assertEqual(task.state, TaskState.ERROR)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CallActivityTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
