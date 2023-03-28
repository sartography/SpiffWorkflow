from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BaseTestCase import BaseTestCase

# NB: I realize this is bad form, but MultiInstanceDMNTest uses a sequential MI task so I'm not adding tests
# for that here.  The task specs are updated the same way, so this should be sufficient.
# I'm not testing the specific of operation here either, because that is pretty extensively tested in the
# main BPMN package

class ParseMultiInstanceTest(BaseTestCase):

    def testCollectionInCardinality(self):

        spec, subprocesses = self.load_workflow_spec('parallel_multiinstance_cardinality.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec)
        start = self.workflow.get_tasks_from_spec_name('Start')[0]
        start.data = {'input_data': [1, 2, 3]}
        self.workflow.do_engine_steps()

        self.save_restore()

        task_spec = self.workflow.get_tasks_from_spec_name('any_task')[0].task_spec
        self.assertEqual(task_spec.data_input.name, 'input_data')
        self.assertEqual(task_spec.data_output.name, 'output_data')
        self.assertEqual(task_spec.input_item.name, 'output_item')
        self.assertEqual(task_spec.output_item.name, 'output_item')

        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 3)

        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 3)
        for task in ready_tasks:
            task.data['output_item'] = task.data['output_item'] * 2
            task.run()

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertDictEqual(self.workflow.data, {'input_data': [1, 2, 3], 'output_data': [2, 4, 6]})

    def testIntegerCardinality(self):

        spec, subprocesses = self.load_workflow_spec('parallel_multiinstance_cardinality.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec)
        task_spec = self.workflow.get_tasks_from_spec_name('any_task')[0].task_spec
        task_spec.cardinality = 'len(input_data)'

        start = self.workflow.get_tasks_from_spec_name('Start')[0]
        start.data = {'input_data': [1, 2, 3]}
        self.workflow.do_engine_steps()

        self.save_restore()

        self.assertEqual(task_spec.data_input, None)
        self.assertEqual(task_spec.input_item.name, 'output_item')

        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 3)
        for task in ready_tasks:
            task.data['output_item'] = task.data['output_item'] * 2
            task.run()

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertDictEqual(self.workflow.data, {'input_data': [1, 2, 3], 'output_data': [0, 2, 4]})

    def testCollection(self):

        spec, subprocesses = self.load_workflow_spec('parallel_multiinstance_collection.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec)
        start = self.workflow.get_tasks_from_spec_name('Start')[0]
        start.data = {'input_data': [1, 2, 3]}
        self.workflow.do_engine_steps()

        self.save_restore()

        task_spec = self.workflow.get_tasks_from_spec_name('any_task')[0].task_spec
        self.assertEqual(task_spec.data_input.name, 'input_data')
        self.assertEqual(task_spec.data_output.name, 'input_data')
        self.assertEqual(task_spec.input_item.name, 'input_item')
        self.assertEqual(task_spec.output_item.name, 'input_item')

        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 3)
        for task in ready_tasks:
            task.data['input_item'] = task.data['input_item'] * 2
            task.run()

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertDictEqual(self.workflow.data, {'input_data': [2, 4, 6]})
