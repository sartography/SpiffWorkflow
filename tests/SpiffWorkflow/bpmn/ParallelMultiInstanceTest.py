from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.exceptions import WorkflowDataException
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.specs.data_spec import TaskDataReference
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase


class BaseTestCase(BpmnWorkflowTestCase):

    def set_io_and_run_workflow(self, data, data_input=None, data_output=None, save_restore=False):

        start = self.workflow.get_next_task(end_at_spec='Start')
        start.data = data

        any_task = self.workflow.get_next_task(spec_name='any_task')
        any_task.task_spec.data_input = TaskDataReference(data_input) if data_input is not None else None
        any_task.task_spec.data_output = TaskDataReference(data_output) if data_output is not None else None

        self.workflow.do_engine_steps()
        ready_tasks = self.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 3)
        while len(ready_tasks) > 0:
            task = ready_tasks[0]
            self.assertEqual(task.task_spec.name, 'any_task [child]')
            self.assertIn('input_item', task.data)
            task.data['output_item'] = task.data['input_item'] * 2
            task.run()
            if save_restore:
                self.save_restore()
            ready_tasks = self.get_ready_user_tasks()
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

    def run_workflow_with_condition(self, data):

        start = self.workflow.get_next_task(end_at_spec='Start')
        start.data = data

        task = self.workflow.get_next_task(spec_name='any_task')
        task.task_spec.condition = "input_item == 2"

        self.workflow.do_engine_steps()
        ready_tasks = self.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 3)
        task = [t for t in ready_tasks if t.data['input_item'] == 2][0]
        task.data['output_item'] = task.data['input_item'] * 2
        task.run()
        self.workflow.do_engine_steps()
        self.workflow.refresh_waiting_tasks()
        
        self.assertTrue(self.workflow.is_completed())
        self.assertEqual(len([ t for t in ready_tasks if t.state == TaskState.CANCELLED]), 2)


class ParallellMultiInstanceExistingOutputTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocess = self.load_workflow_spec('parallel_multiinstance_loop_input.bpmn', 'main')
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


class ParallelMultiInstanceNewOutputTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocess = self.load_workflow_spec('parallel_multiinstance_loop_input.bpmn', 'main')
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
        self.run_workflow_with_condition({'input_data': [1, 2, 3]})
        self.assertDictEqual(self.workflow.data, {
            'input_data': [1, 2, 3],
            'output_data': [4]
        })


class ParallelMultiInstanceUpdateInputTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocess = self.load_workflow_spec('parallel_multiinstance_loop_input.bpmn', 'main')
        self.workflow = BpmnWorkflow(self.spec)

    def testList(self):
        data = { 'input_data': [1, 2, 3]}
        self.set_io_and_run_workflow(data, data_input='input_data', data_output='input_data')
        self.assertDictEqual(self.workflow.data, {'input_data': [2, 4, 6]})

    def testDict(self):
        data = { 'input_data': {'a': 1, 'b': 2, 'c': 3}}
        self.set_io_and_run_workflow(data, data_input='input_data', data_output='input_data')
        self.assertDictEqual(self.workflow.data, {'input_data': {'a': 2, 'b': 4, 'c': 6}})


class ParallelMultiInstanceWithCardinality(BaseTestCase):

    def setUp(self) -> None:
        self.spec, subprocess = self.load_workflow_spec('parallel_multiinstance_cardinality.bpmn', 'main')
        self.workflow = BpmnWorkflow(self.spec)

    def testCardinality(self):
        self.set_io_and_run_workflow({}, data_output='output_data')
        self.assertDictEqual(self.workflow.data, {'output_data': [0, 2, 4]})

    def testCardinalitySaveRestore(self):
        self.set_io_and_run_workflow({}, data_output='output_data', save_restore=True)
        self.assertDictEqual(self.workflow.data, {'output_data': [0, 2, 4]})

    def testCondition(self):
        self.run_workflow_with_condition({})
        self.assertDictEqual(self.workflow.data, {
            'output_data': [4]
        })


class ParallelMultiInstanceTaskTest(BpmnWorkflowTestCase):

    def check_reference(self, reference, name):
        self.assertIsInstance(reference, TaskDataReference)
        self.assertEqual(reference.bpmn_id, name)

    def testParseInputOutput(self):
        spec, subprocess = self.load_workflow_spec('parallel_multiinstance_loop_input.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec)
        task_spec = self.workflow.get_next_task(spec_name='any_task').task_spec
        self.check_reference(task_spec.data_input, 'input_data')
        self.check_reference(task_spec.data_output, 'output_data')
        self.check_reference(task_spec.input_item, 'input_item')
        self.check_reference(task_spec.output_item, 'output_item')
        self.assertIsNone(task_spec.cardinality)

    def testParseCardinality(self):
        spec, subprocess = self.load_workflow_spec('parallel_multiinstance_cardinality.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec)
        task_spec = self.workflow.get_next_task(spec_name='any_task').task_spec
        self.assertIsNone(task_spec.data_input)
        self.assertEqual(task_spec.cardinality, '3')

    def testInvalidBpmn(self):
        with self.assertRaises(ValidationException) as exc:
            spec, subprocess = self.load_workflow_spec('parallel_multiinstance_invalid.bpmn', 'main')
            self.assertEqual(exc.exception.message,
                'A multiinstance task must specify exactly one of cardinality or loop input data reference.')
