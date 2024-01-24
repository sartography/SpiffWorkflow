import os
import time

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine, TaskDataEnvironment
from SpiffWorkflow.bpmn.serializer.migration.exceptions import VersionMigrationError

from .BaseTestCase import BaseTestCase


class Version_1_0_Test(BaseTestCase):

    def test_convert_subprocess(self):
        # The serialization used here comes from NestedSubprocessTest saved at line 25 with version 1.0
        wf = self.deserialize_workflow('v1.0.json')
        # We should be able to finish the workflow from this point
        ready_tasks = wf.get_tasks(state=TaskState.READY)
        self.assertEqual('Action3', ready_tasks[0].task_spec.bpmn_name)
        ready_tasks[0].run()
        wf.do_engine_steps()
        wf.refresh_waiting_tasks()
        wf.do_engine_steps()
        wf.refresh_waiting_tasks()
        wf.do_engine_steps()
        self.assertEqual(True, wf.is_completed())


class Version_1_1_Test(BaseTestCase):

    def test_timers(self):
        wf = self.deserialize_workflow('v1.1-timers.json')
        wf.script_engine = PythonScriptEngine(environment=TaskDataEnvironment({"time": time}))
        wf.refresh_waiting_tasks()
        wf.do_engine_steps()
        wf.refresh_waiting_tasks()
        wf.do_engine_steps()
        self.assertTrue(wf.is_completed())

    def test_convert_data_specs(self):
        wf = self.deserialize_workflow('v1.1-data.json')
        wf.do_engine_steps()
        wf.refresh_waiting_tasks()
        wf.do_engine_steps()
        self.assertTrue(wf.is_completed())

    def test_convert_exclusive_gateway(self):
        wf = self.deserialize_workflow('v1.1-gateways.json')
        wf.do_engine_steps()
        task = wf.get_next_task(spec_name='Gateway_askQuestion')
        self.assertEqual(len(task.task_spec.cond_task_specs), 2)
        ready_task = wf.get_tasks(state=TaskState.READY, manual=True)[0]
        ready_task.data['NeedClarification'] = 'Yes'
        ready_task.run()
        wf.do_engine_steps()
        ready_task = wf.get_tasks(state=TaskState.READY, manual=True)[0]
        self.assertEqual(ready_task.task_spec.name, 'Activity_A2')

    def test_check_multiinstance(self):
        with self.assertRaises(VersionMigrationError) as ctx:
            wf = self.deserialize_workflow('v1.1-multi.json')
            self.assertEqual(ctx.exception.message, "This workflow cannot be migrated because it contains MultiInstance Tasks")

    def test_remove_loop_reset(self):
        wf = self.deserialize_workflow('v1.1-loop-reset.json')
        # Allow 3 seconds max to allow this test to complete (there are 20 loops with a 0.1s timer)
        end = time.time() + 3
        while not wf.is_completed() and time.time() < end:
            wf.do_engine_steps()
            wf.refresh_waiting_tasks()
        self.assertTrue(wf.is_completed())
        self.assertEqual(wf.last_task.data['counter'], 20)

    def test_update_task_states(self):
        wf = self.deserialize_workflow('v1.1-task-states.json')
        start = wf.get_tasks(end_at_spec='Start')[0]
        self.assertEqual(start.state, TaskState.COMPLETED)
        signal = wf.get_next_task(spec_name='signal')
        self.assertEqual(signal.state, TaskState.CANCELLED)
        ready_tasks = wf.get_tasks(state=TaskState.READY)
        while len(ready_tasks) > 0:
            ready_tasks[0].run()
            ready_tasks = wf.get_tasks(state=TaskState.READY)
        self.assertTrue(wf.is_completed())


class Version_1_2_Test(BaseTestCase):

    def test_remove_boundary_events(self):
        wf = self.deserialize_workflow('v1.2-boundary-events.json')
        ready_tasks = wf.get_tasks(state=TaskState.READY)
        ready_tasks[0].set_data(**{'value': 'asdf'})
        ready_tasks[0].run()
        wf.do_engine_steps()
        ready_tasks = wf.get_tasks(state=TaskState.READY)
        ready_tasks[0].set_data(**{'quantity': 2})
        ready_tasks[0].run()
        wf.do_engine_steps()
        self.assertIn('value', wf.last_task.data)

        # Check that workflow and next task completed
        subprocess = wf.get_next_task(spec_name='Subprocess')
        self.assertEqual(subprocess.state, TaskState.COMPLETED)
        print_task = wf.get_next_task(spec_name="Activity_Print_Data")
        self.assertEqual(print_task.state, TaskState.COMPLETED)

        # Check that the boundary events were cancelled
        cancel_task = wf.get_next_task(spec_name="Catch_Cancel_Event")
        self.assertEqual(cancel_task.state, TaskState.CANCELLED)
        error_1_task = wf.get_next_task(spec_name="Catch_Error_1")
        self.assertEqual(error_1_task.state, TaskState.CANCELLED)
        error_none_task = wf.get_next_task(spec_name="Catch_Error_None")
        self.assertEqual(error_none_task.state, TaskState.CANCELLED)

    def test_remove_noninterrupting_boundary_events(self):
        wf = self.deserialize_workflow('v1.2-boundary-events-noninterrupting.json')
        wf.get_next_task(spec_name='sid-D3365C47-2FAE-4D17-98F4-E68B345E18CE').run()
        wf.do_engine_steps()
        self.assertEqual(1, len(wf.get_tasks(state=TaskState.READY)))
        self.assertEqual(3, len(wf.get_tasks(state=TaskState.WAITING)))

        wf.get_next_task(spec_name='sid-6FBBB56D-00CD-4C2B-9345-486986BB4992').run()
        wf.do_engine_steps()
        self.assertTrue(wf.is_completed())
