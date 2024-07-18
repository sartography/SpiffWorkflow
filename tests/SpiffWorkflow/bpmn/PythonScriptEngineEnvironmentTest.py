import json

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine
from SpiffWorkflow.bpmn.script_engine.python_environment import BasePythonScriptEngineEnvironment, TaskDataEnvironment

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

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
        return True

    def user_defined_values(self):
        return {k: v for k, v in self.environment.items() if k not in self.globals}


class AsyncScriptEnvironment(TaskDataEnvironment):

    def execute(self, script, context, external_methods=None):
        super().execute(script, context, external_methods)
        return None 


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

        self.assertEqual(task_data_len, 2)
        self.assertEqual(d_len, 512*3)
        self.assertEqual(d_uniques, {"a", "b", "c"})

    def _get_task_data_len(self):
        tasks_to_check = self.workflow.get_tasks(state=TaskState.FINISHED_MASK)
        task_data = [task.data for task in tasks_to_check]
        task_data_to_check = list(filter(len, task_data))
        task_data_len = len(json.dumps(task_data_to_check))
        return task_data_len


class StartedTaskTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('script-start.bpmn', 'Process_cozt5fu')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testStartedState(self):
        script_engine_environemnt = AsyncScriptEnvironment()
        script_engine = PythonScriptEngine(environment=script_engine_environemnt)
        self.workflow.script_engine = script_engine
        self.workflow.do_engine_steps()
        script_task = self.workflow.get_next_task(spec_name='script')
        self.assertEqual(script_task.state, TaskState.STARTED)
        script_task.complete()
        manual_task = self.workflow.get_next_task(spec_name='manual')
        manual_task.run()
        self.workflow.do_engine_steps()
        end = self.workflow.get_next_task(spec_name='End')
        self.assertDictEqual(end.data, {'x': 1, 'y': 2, 'z': 3})
        self.assertTrue(self.workflow.completed)
