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
        with open(fn) as fh:
            wf = self.serializer.deserialize_json(fh.read())
        # We should be able to finish the workflow from this point
        ready_tasks = wf.get_tasks(TaskState.READY)
        self.assertEqual('Action3', ready_tasks[0].task_spec.description)
        ready_tasks[0].run()
        wf.do_engine_steps()
        wf.refresh_waiting_tasks()
        wf.do_engine_steps()
        wf.refresh_waiting_tasks()
        wf.do_engine_steps()
        self.assertEqual(True, wf.is_completed())


class Version_1_1_Test(BaseTestCase):

    def test_timers(self):
        fn = os.path.join(self.DATA_DIR, 'serialization', 'v1.1-timers.json')
        wf = self.serializer.deserialize_json(open(fn).read())
        wf.script_engine = PythonScriptEngine(environment=TaskDataEnvironment({"time": time}))
        wf.refresh_waiting_tasks()
        wf.do_engine_steps()
        wf.refresh_waiting_tasks()
        wf.do_engine_steps()
        self.assertTrue(wf.is_completed())

    def test_convert_data_specs(self):
        fn = os.path.join(self.DATA_DIR, 'serialization', 'v1.1-data.json')
        wf = self.serializer.deserialize_json(open(fn).read())
        wf.do_engine_steps()
        wf.refresh_waiting_tasks()
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
        ready_task.run()
        wf.do_engine_steps()
        ready_task = wf.get_ready_user_tasks()[0]
        self.assertEqual(ready_task.task_spec.name, 'Activity_A2')

    def test_check_multiinstance(self):
        fn = os.path.join(self.DATA_DIR, 'serialization', 'v1.1-multi.json')
        with self.assertRaises(VersionMigrationError) as ctx:
            wf = self.serializer.deserialize_json(open(fn).read())
            self.assertEqual(ctx.exception.message, "This workflow cannot be migrated because it contains MultiInstance Tasks")

    def test_remove_loop_reset(self):
        fn = os.path.join(self.DATA_DIR, 'serialization', 'v1.1-loop-reset.json')
        wf = self.serializer.deserialize_json(open(fn).read())
        # Allow 3 seconds max to allow this test to complete (there are 20 loops with a 0.1s timer)
        end = time.time() + 3
        while not wf.is_completed() and time.time() < end:
            wf.do_engine_steps()
            wf.refresh_waiting_tasks()
        self.assertTrue(wf.is_completed())
        self.assertEqual(wf.last_task.data['counter'], 20)
