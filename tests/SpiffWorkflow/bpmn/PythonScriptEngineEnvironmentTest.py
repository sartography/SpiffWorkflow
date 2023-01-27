import json

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import BasePythonScriptEngineEnvironment
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.task import TaskState

def example_global():
    pass

class NonTaskDataExampleEnvironment(BasePythonScriptEngineEnvironment):
    def __init__(self, environment_globals, environment):
        self.environment = environment
        self.environment.update(environment_globals)
        super().__init__(environment_globals)

    def evaluate(self, expression, context, external_methods=None):
        pass

    def execute(self, script, context, external_methods=None):
        self.environment.update(context)
        self.environment.update(external_methods or {})
        exec(script, self.environment)
        self.environment = {k: v for k, v in self.environment.items() if k not in external_methods}

    def user_defined_values(self):
        return {k: v for k, v in self.environment.items() if k not in self.globals}

class PythonScriptEngineEnvironmentTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('task_data_size.bpmn', 'Process_ccz6oq2')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testTaskDataSizeWithDefaultPythonScriptEngine(self):
        self.workflow.do_engine_steps()

        self.assertIn("a", self.workflow.data)
        self.assertIn("b", self.workflow.data)
        self.assertIn("c", self.workflow.data)
        self.assertIn("d", self.workflow.data)

        task_data_len = self._get_task_data_len()
        d_uniques = set(self.workflow.data["d"])
        d_len = len(self.workflow.data["d"])

        self.assertGreater(task_data_len, 15000)
        self.assertEqual(d_len, 512*3)
        self.assertEqual(d_uniques, {"a", "b", "c"})

    def testTaskDataSizeWithNonTaskDataEnvironmentBasedPythonScriptEngine(self):
        script_engine_environment = NonTaskDataExampleEnvironment({"example_global": example_global}, {})
        script_engine = PythonScriptEngine(environment=script_engine_environment)
        self.workflow.script_engine = script_engine

        self.workflow.do_engine_steps()
        self.workflow.data.update(script_engine.environment.user_defined_values())

        self.assertIn("a", self.workflow.data)
        self.assertIn("b", self.workflow.data)
        self.assertIn("c", self.workflow.data)
        self.assertIn("d", self.workflow.data)
        self.assertNotIn("example_global", self.workflow.data)

        task_data_len = self._get_task_data_len()
        d_uniques = set(self.workflow.data["d"])
        d_len = len(self.workflow.data["d"])

        self.assertLess(task_data_len, 50)
        self.assertEqual(d_len, 512*3)
        self.assertEqual(d_uniques, {"a", "b", "c"})

    def _get_task_data_len(self):
        tasks_to_check = self.workflow.get_tasks(TaskState.FINISHED_MASK)
        task_data = [task.data for task in tasks_to_check]
        task_data_len = len(json.dumps(task_data))
        return task_data_len

