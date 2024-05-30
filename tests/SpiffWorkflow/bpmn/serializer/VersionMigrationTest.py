import os
import time
from uuid import UUID

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine, TaskDataEnvironment
from SpiffWorkflow.bpmn.serializer.exceptions import VersionMigrationError

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

    def test_update_data_objects(self):

        # Workflow source: serialized from DataObjectTest after the subprocess has been created
        wf = self.deserialize_workflow('v1.2-data-objects.json')

        # Check that the data objects were removed from the subprocess
        sp_task = wf.get_next_task(spec_name='subprocess')
        sp = wf.get_subprocess(sp_task)
        self.assertNotIn('obj_1', sp.data)
        self.assertNotIn('data_objects', sp.data)
        sp_spec = wf.subprocess_specs.get('subprocess')
        self.assertEqual(len(sp_spec.data_objects), 0)

        # Make sure we can complete the process as we did in the original test
        wf.do_engine_steps()
        ready_tasks = wf.get_tasks(state=TaskState.READY)
        self.assertEqual(ready_tasks[0].data['obj_1'], 'hello')
        ready_tasks[0].data['obj_1'] = 'hello again'
        ready_tasks[0].run()
        wf.do_engine_steps()
        # The data object is not in the task data
        self.assertNotIn('obj_1', sp_task.data)
        # The update should persist in the main process
        self.assertEqual(wf.data_objects['obj_1'], 'hello again')

    def test_update_nested_data_objects(self):

        wf = self.deserialize_workflow('v1.2-data-objects-nested.json')
        self.assertIn('top_level_data_object', wf.data_objects)
        self.assertNotIn('sub_level_data_object_two', wf.data)
        self.assertNotIn('sub_level_data_object_three', wf.data)

        process_sub = wf.subprocesses[UUID('270d76e0-c1fe-4add-b58e-d5a51214a37b')]
        call_sub = wf.subprocesses[UUID('d0c6a2d9-9a43-4ccd-b4e3-ea62872f15ed')]

        self.assertNotIn('top_level_data_object', process_sub.spec.data_objects)
        self.assertNotIn('top_level_data_object', call_sub.spec.data_objects)
        self.assertIn('sub_level_data_object_two', process_sub.spec.data_objects)
        self.assertNotIn('sub_level_data_object_two', call_sub.spec.data_objects)
        self.assertIn('sub_level_data_object_three', call_sub.spec.data_objects)
        self.assertNotIn('sub_level_data_object_three', process_sub.spec.data_objects)

        self.assertNotIn('top_level_data_object', process_sub.data_objects)
        self.assertNotIn('top_level_data_object', call_sub.data_objects)

        self.assertIn('sub_level_data_object_two', process_sub.data_objects)
        self.assertNotIn('sub_level_data_object_two', call_sub.data_objects)
        self.assertIn('sub_level_data_object_three', call_sub.data_objects)
        self.assertNotIn('sub_level_data_object_three', process_sub.data_objects)

class Version_1_3_Test(BaseTestCase):

    def test_update_mi_states(self):

        wf = self.deserialize_workflow('v1.3-mi-states.json')

        any_task = wf.get_next_task(spec_name='any_task')
        task_info = any_task.task_spec.task_info(any_task)
        instance_map = task_info['instance_map']

        self.assertEqual(len(wf.get_tasks(state=TaskState.WAITING)), 0)

        ready_tasks = wf.get_tasks(state=TaskState.READY, manual=True)
        self.assertEqual(len(ready_tasks), 1)
        while len(ready_tasks) > 0:
            task = ready_tasks[0]
            task_info = task.task_spec.task_info(task)
            self.assertEqual(task.task_spec.name, 'any_task [child]')
            self.assertIn('input_item', task.data)
            self.assertEqual(instance_map[task_info['instance']], str(task.id))
            task.data['output_item'] = task.data['input_item'] * 2
            task.run()
            ready_tasks = wf.get_tasks(state=TaskState.READY, manual=True)
        wf.refresh_waiting_tasks()
        wf.do_engine_steps()

        any_task = wf.get_next_task(spec_name='any_task')
        task_info = any_task.task_spec.task_info(any_task)
        self.assertEqual(len(task_info['completed']), 3)
        self.assertEqual(len(task_info['running']), 0)
        self.assertEqual(len(task_info['future']), 0)
        self.assertTrue(wf.is_completed())
