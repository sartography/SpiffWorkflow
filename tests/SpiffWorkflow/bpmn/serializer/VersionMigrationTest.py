import os
import time

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment
from SpiffWorkflow.bpmn.serializer.migration.exceptions import VersionMigrationError

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

    def test_convert_exclusive_gateway(self):
        fn = os.path.join(self.DATA_DIR, 'serialization', 'v1.1-gateways.json')
        wf = self.serializer.deserialize_json(open(fn).read())
        wf.do_engine_steps()
        task = wf.get_tasks_from_spec_name('Gateway_askQuestion')[0]
        self.assertEqual(len(task.task_spec.cond_task_specs), 2)
        ready_task = wf.get_ready_user_tasks()[0]
        ready_task.data['NeedClarification'] = 'Yes'
        ready_task.complete()
        wf.do_engine_steps()
        ready_task = wf.get_ready_user_tasks()[0]
        self.assertEqual(ready_task.task_spec.name, 'Activity_A2')

    def test_check_multiinstance(self):
        fn = os.path.join(self.DATA_DIR, 'serialization', 'v1.1-multi.json')
        with self.assertRaises(VersionMigrationError) as ctx:
            wf = self.serializer.deserialize_json(open(fn).read())
            self.assertEqual(ctx.exception.message, "This workflow cannot be migrated because it contains MultiInstance Tasks")