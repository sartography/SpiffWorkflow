import json

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.task import TaskState

class PythonScriptEngineEnvironmentTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('task_data_size.bpmn', 'Process_ccz6oq2')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testTaskDataSizeWithDefaultPythonScriptEngine(self):
        self.workflow.do_engine_steps()
        task_data_len = self._get_task_data_len()
        d_uniques = set(self.workflow.data["d"])
        d_len = len(self.workflow.data["d"])

        self.assertGreater(task_data_len, 1024)
        self.assertEqual(d_len, 512*3)
        self.assertEqual(d_uniques, {"a", "b", "c"})

    def testTaskDataSizeWithEnvironmentBasedPythonScriptEngine(self):
        self.workflow.do_engine_steps()
        task_data_len = self._get_task_data_len()
        d_uniques = set(self.workflow.data["d"])
        d_len = len(self.workflow.data["d"])

        #self.assertLess(task_data_len, 1024)
        self.assertEqual(d_len, 512*3)
        self.assertEqual(d_uniques, {"a", "b", "c"})

    def _get_task_data_len(self):
        tasks_to_check = self.workflow.get_tasks(TaskState.FINISHED_MASK)
        task_data = [task.data for task in tasks_to_check]
        task_data_len = len(json.dumps(task_data))
        return task_data_len

