from SpiffWorkflow.bpmn.exceptions import WorkflowDataException
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.specs.data_spec import TaskDataReference

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase


class BaseTestCase(BpmnWorkflowTestCase):

    def set_io_and_run_workflow(self, data, data_input=None, data_output=None, save_restore=False):

        start = self.workflow.get_next_task(end_at_spec='Start')
        start.data = data

        any_task = self.get_first_task_from_spec_name('any_task')
        any_task.task_spec.data_input = TaskDataReference(data_input) if data_input is not None else None
        any_task.task_spec.data_output = TaskDataReference(data_output) if data_output is not None else None

        self.workflow.do_engine_steps()
        self.workflow.refresh_waiting_tasks()
        ready_tasks = self.get_ready_user_tasks()

        while len(ready_tasks) > 0:
            self.assertEqual(len(ready_tasks), 1)
            task = ready_tasks[0]
            self.assertEqual(task.task_spec.name, 'any_task [child]')
            self.assertIn('input_item', task.data)
            task.data['output_item'] = task.data['input_item'] * 2
            task.run()
            if save_restore:
                self.save_restore()
            ready_tasks = self.get_ready_user_tasks()

        self.workflow.do_engine_steps()
        children = self.get_tasks_from_spec_name('any_task [child]')
        self.assertEqual(len(children), 3)
        self.assertTrue(self.workflow.is_completed()) 

    def run_workflow_with_condition(self, data, condition):

        start = self.workflow.get_next_task(end_at_spec='Start')
        start.data = data

        task = self.get_first_task_from_spec_name('any_task')
        task.task_spec.condition = condition

        self.workflow.do_engine_steps()
        self.workflow.refresh_waiting_tasks()
        ready_tasks = self.get_ready_user_tasks()

        while len(ready_tasks) > 0:
            ready = ready_tasks[0]
            self.assertEqual(ready.task_spec.name, 'any_task [child]')
            self.assertIn('input_item', ready.data)
            ready.data['output_item'] = ready.data['input_item'] * 2
            ready.run()
            self.workflow.do_engine_steps()
            self.workflow.refresh_waiting_tasks()
            ready_tasks = self.get_ready_user_tasks()

        self.workflow.do_engine_steps()
        children = self.get_tasks_from_spec_name('any_task [child]')
        self.assertEqual(len(children), 2)
        self.assertTrue(self.workflow.is_completed())


class SequentialMultiInstanceExistingOutputTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocess = self.load_workflow_spec('sequential_multiinstance_loop_input.bpmn', 'main')
        self.workflow = BpmnWorkflow(self.spec)

    def testListWithDictOutput(self):
        data = {
            'input_data': [1, 2, 3],
            'output_data': {},
        }
        self.set_io_and_run_workflow(data, data_input='input_data', data_output='output_data')
        self.assertDictEqual(self.workflow.data, {
            'input_data': [1, 2, 3],
            'output_data': {0: 2, 1: 4, 2: 6},
        })

    def testDictWithListOutput(self):
        data = {
            'input_data': {'a': 1, 'b': 2, 'c': 3},
            'output_data': [],
        }
        self.set_io_and_run_workflow(data, data_input='input_data', data_output='output_data')
        self.assertDictEqual(self.workflow.data, {
            'input_data': {'a': 1, 'b': 2, 'c': 3},
            'output_data': [2, 4, 6],
        })

    def testNonEmptyOutput(self):
        with self.assertRaises(WorkflowDataException) as exc:
            data = {
                'input_data': [1, 2, 3],
                'output_data': [1, 2, 3],
            }
            self.set_io_and_run_workflow(data, data_input='input_data', data_output='output_data')
            self.assertEqual(exc.exception.message, 
                "If the input is not being updated in place, the output must be empty or it must be a map (dict)")

    def testInvalidOutputType(self):
        with self.assertRaises(WorkflowDataException) as exc:
            data = {
                'input_data': set([1, 2, 3]),
                'output_data': set(),
            }
            self.set_io_and_run_workflow(data, data_input='input_data', data_output='output_data')
            self.assertEqual(exc.exception.message, "Only a mutable map (dict) or sequence (list) can be used for output")


class SequentialMultiInstanceNewOutputTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocess = self.load_workflow_spec('sequential_multiinstance_loop_input.bpmn', 'main')
        self.workflow = BpmnWorkflow(self.spec)

    def testList(self):
        data = {'input_data': [1, 2, 3]}
        self.set_io_and_run_workflow(data, data_input='input_data', data_output='output_data')
        self.assertDictEqual(self.workflow.data, {
            'input_data': [1, 2, 3],
            'output_data': [2, 4, 6]
        })

    def testListSaveRestore(self):
        data = {'input_data': [1, 2, 3]}
        self.set_io_and_run_workflow(data, data_input='input_data', data_output='output_data', save_restore=True)
        self.assertDictEqual(self.workflow.data, {
            'input_data': [1, 2, 3],
            'output_data': [2, 4, 6]
        })

    def testDict(self):
        data = {'input_data': {'a': 1, 'b': 2, 'c': 3} }
        self.set_io_and_run_workflow(data, data_input='input_data', data_output='output_data')
        self.assertDictEqual(self.workflow.data, {
            'input_data': {'a': 1, 'b': 2, 'c': 3},
            'output_data': {'a': 2, 'b': 4, 'c': 6}
        })        

    def testDictSaveRestore(self):
        data = {'input_data': {'a': 1, 'b': 2, 'c': 3} }
        self.set_io_and_run_workflow(data, data_input='input_data', data_output='output_data', save_restore=True)
        self.assertDictEqual(self.workflow.data, {
            'input_data': {'a': 1, 'b': 2, 'c': 3},
            'output_data': {'a': 2, 'b': 4, 'c': 6}
        })

    def testSet(self):
        data = {'input_data': set([1, 2, 3])}
        self.set_io_and_run_workflow(data, data_input='input_data', data_output='output_data')
        self.assertDictEqual(self.workflow.data, {
            'input_data': set([1, 2, 3]),
            'output_data': [2, 4, 6]
        })

    def testEmptyCollection(self):

        start = self.workflow.get_next_task(end_at_spec='Start')
        start.data = {'input_data': []}
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertDictEqual(self.workflow.data, {'input_data': [], 'output_data': []})

    def testCondition(self):
        self.run_workflow_with_condition({'input_data': [1, 2, 3]}, "input_item == 2")
        self.assertDictEqual(self.workflow.data, {
            'input_data': [1, 2, 3],
            'output_data': [2, 4]
        })


class SequentialMultiInstanceUpdateInputTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocess = self.load_workflow_spec('sequential_multiinstance_loop_input.bpmn', 'main')
        self.workflow = BpmnWorkflow(self.spec)

    def testList(self):
        data = { 'input_data': [1, 2, 3]}
        self.set_io_and_run_workflow(data, data_input='input_data', data_output='input_data')
        self.assertDictEqual(self.workflow.data, {'input_data': [2, 4, 6]})

    def testDict(self):
        data = { 'input_data': {'a': 1, 'b': 2, 'c': 3}}
        self.set_io_and_run_workflow(data, data_input='input_data', data_output='input_data')
        self.assertDictEqual(self.workflow.data, {'input_data': {'a': 2, 'b': 4, 'c': 6}})


class SequentialMultiInstanceWithCardinality(BaseTestCase):

    def setUp(self) -> None:
        self.spec, subprocess = self.load_workflow_spec('sequential_multiinstance_cardinality.bpmn', 'main')
        self.workflow = BpmnWorkflow(self.spec)

    def testCardinality(self):
        self.set_io_and_run_workflow({}, data_output='output_data')
        self.assertDictEqual(self.workflow.data, {'output_data': [0, 2, 4]})

    def testCardinalitySaveRestore(self):
        self.set_io_and_run_workflow({}, data_output='output_data', save_restore=True)
        self.assertDictEqual(self.workflow.data, {'output_data': [0, 2, 4]})

    def testCondition(self):
        self.run_workflow_with_condition({}, "input_item == 1")
        self.assertDictEqual(self.workflow.data, {
            'output_data': [0, 2]
        })
