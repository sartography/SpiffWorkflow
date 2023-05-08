from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskException
from SpiffWorkflow.task import TaskState

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class CallActivityTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('call_activity_*.bpmn', 'Process_8200379')

    def test_data_persists_through_call_activity(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.workflow.do_engine_steps()
        self.complete_subworkflow()
        self.assertDictEqual(self.workflow.data, {'pre_var': 'some string', 'my_var': 'World', 'my_other_var': 'Mike'})

    def test_call_activity_has_same_script_engine(self):
        class CustomScriptEngine(PythonScriptEngine):
            pass

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses, script_engine=CustomScriptEngine())
        self.workflow.do_engine_steps()
        self.complete_subworkflow()
        self.assertTrue(self.workflow.is_completed())
        self.assertIsInstance(self.workflow.script_engine, CustomScriptEngine)

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

    def test_order_of_tasks_in_get_task_is_call_acitivty_task_first_then_sub_tasks(self):
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.workflow.do_engine_steps()
        tasks = self.workflow.get_tasks()
        def index_of(name):
            return [i for i, x in enumerate(tasks) if x.task_spec.name == name][0]

        self.assertLess(index_of('Activity_Call_Activity'), index_of('Start_Called_Activity'))
        self.assertLess(index_of('Activity_Call_Activity'), index_of('Sub_Bpmn_Task'))
        self.assertLess(index_of('Activity_Call_Activity'), index_of('End_Called_Activity'))
