from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
from SpiffWorkflow.bpmn.exceptions import WorkflowDataException
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

class DataStoreReferenceTest(BpmnWorkflowTestCase):

    def _testParsesDataStoreReferenceWithInputsAndOutputs(self):
        spec, subprocesses = self.load_workflow_spec('data_store.bpmn', 'JustDataStoreRef')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testCanSaveRestoreDataStoreReferenceWithInputsAndOutputs(self):
        spec, subprocesses = self.load_workflow_spec('data_store.bpmn', 'JustDataStoreRef')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.save_restore()
        self.workflow.do_engine_steps()
        self.save_restore()

        last_script_task_data = self.workflow.get_tasks_from_spec_name("Activity_1skgyn9")[0].data
        self.assertEqual(len(last_script_task_data), 1)
        self.assertEqual(last_script_task_data["x"], "Sue")

    def _testCanInterpretDataStoreReferenceWithInputsAndOutputs(self):
        spec, subprocesses = self.load_workflow_spec('data_store.bpmn', 'JustDataStoreRef')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

        last_script_task_data = self.workflow.get_tasks_from_spec_name("Activity_1skgyn9")[0].data
        self.assertEqual(len(last_script_task_data), 1)
        self.assertEqual(last_script_task_data["x"], "Sue")


# TODO: see if we need to handle any more of the cases below

#    def setUp(self):
#        self.spec, self.subprocesses = self.load_workflow_spec('data_object.bpmn', 'Process')
#
#    def testDataObjectReferences(self):
#        self.actual_test(False)
#
#    def testDataObjectSerialization(self):
#        self.actual_test(True)
#
#    def testMissingDataInput(self):
#
#        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
#        self.workflow.do_engine_steps()
#
#        # Add the data so that we can advance the workflow
#        ready_tasks = self.workflow.get_ready_user_tasks()
#        ready_tasks[0].data = { 'obj_1': 'hello' }
#        ready_tasks[0].complete()
#
#        # Remove the data before advancing
#        ready_tasks = self.workflow.get_ready_user_tasks()
#        self.workflow.data.pop('obj_1')
#        with self.assertRaises(WorkflowDataException) as exc:
#            ready_tasks[0].complete()
#            self.assertEqual(exc.data_output.name, 'obj_1')
#
#    def testMissingDataOutput(self):
#
#        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
#        self.workflow.do_engine_steps()
#        ready_tasks = self.workflow.get_ready_user_tasks()
#        with self.assertRaises(WorkflowDataException) as exc:
#            ready_tasks[0].complete()
#            self.assertEqual(exc.data_output.name, 'obj_1')
#
#    def actual_test(self, save_restore):
#
#        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
#        self.workflow.do_engine_steps()
#
#        # Set up the data
#        ready_tasks = self.workflow.get_ready_user_tasks()
#        ready_tasks[0].data = { 'obj_1': 'hello' }
#        ready_tasks[0].complete()
#        # After task completion, obj_1 should be copied out of the task into the workflow
#        self.assertNotIn('obj_1', ready_tasks[0].data)
#        self.assertIn('obj_1', self.workflow.data)
#
#        if save_restore:
#            self.save_restore()
#
#        # Set a value for obj_1 in the task data again
#        ready_tasks = self.workflow.get_ready_user_tasks()
#        ready_tasks[0].data = { 'obj_1': 'hello again' }
#        ready_tasks[0].complete()
#
#        # Check to make sure we use the workflow value instead of the value we set
#        ready_tasks = self.workflow.get_ready_user_tasks()
#        self.assertEqual(ready_tasks[0].data['obj_1'], 'hello')
#        # Modify the value in the task
#        ready_tasks[0].data = { 'obj_1': 'hello again' }
#        ready_tasks[0].complete()
#        # We did not set an output data reference so obj_1 should remain unchanged in the workflow data
#        # and be removed from the task data
#        self.assertNotIn('obj_1', ready_tasks[0].data)
#        self.assertEqual(self.workflow.data['obj_1'], 'hello')
#
#        # Make sure data objects can be copied in and out of a subprocess
#        self.workflow.do_engine_steps()
#        ready_tasks = self.workflow.get_ready_user_tasks()
#        self.assertEqual(ready_tasks[0].data['obj_1'], 'hello')
#        ready_tasks[0].complete()
#        self.workflow.do_engine_steps()
#        sp = self.workflow.get_tasks_from_spec_name('subprocess')[0]
#        self.assertNotIn('obj_1', sp.data)
