from .BpmnWorkflowTestCase import BpmnWorkflowTestCase
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.exceptions import WorkflowDataException


class DataObjectReferenceTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('data_object.bpmn', 'Process')

    def testDataObjectReferences(self):
        self.actual_test(False)

    def testDataObjectSerialization(self):
        self.actual_test(True)

    def testMissingDataInput(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.workflow.do_engine_steps()

        # Add the data so that we can advance the workflow
        ready_tasks = self.get_ready_user_tasks()
        ready_tasks[0].data = { 'obj_1': 'hello' }
        ready_tasks[0].run()

        # Remove the data before advancing
        ready_tasks = self.get_ready_user_tasks()
        self.workflow.data_objects.pop('obj_1')
        with self.assertRaises(WorkflowDataException) as exc:
            ready_tasks[0].run()
            self.assertEqual(exc.data_output.name, 'obj_1')

    def testMissingDataOutput(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.workflow.do_engine_steps()
        ready_tasks = self.get_ready_user_tasks()
        with self.assertRaises(WorkflowDataException) as exc:
            ready_tasks[0].run()
            self.assertEqual(exc.data_output.name, 'obj_1')

    def actual_test(self, save_restore):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.workflow.do_engine_steps()

        # Set up the data
        ready_tasks = self.get_ready_user_tasks()
        ready_tasks[0].data = { 'obj_1': 'hello' }
        ready_tasks[0].run()
        # After task completion, obj_1 should be copied out of the task into the workflow
        self.assertNotIn('obj_1', ready_tasks[0].data)
        self.assertIn('obj_1', self.workflow.data_objects)

        if save_restore:
            self.save_restore()

        # Set a value for obj_1 in the task data again
        ready_tasks = self.get_ready_user_tasks()
        ready_tasks[0].data = { 'obj_1': 'hello again' }
        ready_tasks[0].run()

        # Check to make sure we use the workflow value instead of the value we set
        ready_tasks = self.get_ready_user_tasks()
        self.assertEqual(ready_tasks[0].data['obj_1'], 'hello')
        # Modify the value in the task
        ready_tasks[0].data = { 'obj_1': 'hello again' }
        ready_tasks[0].run()
        # We did not set an output data reference so obj_1 should remain unchanged in the workflow data
        # and be removed from the task data
        self.assertNotIn('obj_1', ready_tasks[0].data)
        self.assertEqual(self.workflow.data_objects['obj_1'], 'hello')

        if save_restore:
            self.save_restore()

        # Make sure data objects are accessible inside a subprocess
        self.workflow.do_engine_steps()
        ready_tasks = self.get_ready_user_tasks()
        self.assertEqual(ready_tasks[0].data['obj_1'], 'hello')
        ready_tasks[0].data['obj_1'] = 'hello again'
        ready_tasks[0].run()
        self.workflow.do_engine_steps()
        sp = self.workflow.get_next_task(spec_name='subprocess')
        # It was copied out
        self.assertNotIn('obj_1', sp.data)
        # The update should persist in the main process
        self.assertEqual(self.workflow.data_objects['obj_1'], 'hello again')

class DataObjectGatewayTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('data_object_gateway.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()
    
    def testExpression(self):
        task = self.get_ready_user_tasks()[0]
        # Set the data object
        task.data = {'val': True}
        task.run()
        # The gateway depends on the value of the data object
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.completed)
        completed = [task.task_spec.name for task in self.workflow.get_tasks()]
        self.assertIn('yes', completed)
        self.assertNotIn('no', completed)
        # The data object was removed by the script engine
        self.assertNotIn('val', self.workflow.last_task.data)
