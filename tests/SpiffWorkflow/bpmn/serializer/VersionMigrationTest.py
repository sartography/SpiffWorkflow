import os
import time

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment

from .BaseTestCase import BaseTestCase


class Version_1_0_Test(BaseTestCase):

    SERIALIZER_VERSION = "1.2"

    def test_convert_subprocess(self):
        # The serialization used here comes from NestedSubprocessTest saved at line 25 with version 1.0
        fn = os.path.join(self.DATA_DIR, 'serialization', 'v1.0.json')
        wf = self.serializer.deserialize_json(open(fn).read())
        # We should be able to finish the workflow from this point
        ready_tasks = wf.get_tasks(TaskState.READY)
        self.assertEqual('Action3', ready_tasks[0].task_spec.description)
        ready_tasks[0].complete()
        wf.do_engine_steps()
        self.assertEqual(True, wf.is_completed())


class Version_1_1_Test(BaseTestCase):

    def test_timers(self):
        fn = os.path.join(self.DATA_DIR, 'serialization', 'v1.1-timers.json')
        wf = self.serializer.deserialize_json(open(fn).read())
        wf.script_engine = PythonScriptEngine(environment=TaskDataEnvironment({"time": time}))
        wf.refresh_waiting_tasks()
        wf.do_engine_steps()
        self.assertTrue(wf.is_completed())

    def test_convert_data_specs(self):
        fn = os.path.join(self.DATA_DIR, 'serialization', 'v1.1-data.json')
        wf = self.serializer.deserialize_json(open(fn).read())
        wf.do_engine_steps()
        self.assertTrue(wf.is_completed())