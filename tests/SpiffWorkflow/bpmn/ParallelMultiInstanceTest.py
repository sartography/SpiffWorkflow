from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.exceptions import WorkflowDataException
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase


class BaseTestCase(BpmnWorkflowTestCase):

    def set_data_and_run_workflow(self, script):
        set_data = self.workflow.get_tasks_from_spec_name('set_data')[0]
        set_data.task_spec.script = script
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 3)
        for task in ready_tasks:
            self.assertEqual(task.task_spec.name, 'any_task [child]')
            self.assertIn('input_item', task.data)
            task.data['output_item'] = task.data['input_item'] * 2
            task.complete()
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()


class ParallellMultiInstanceExistingOutputTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocess = self.load_workflow_spec('parallel_multiinstance_existing_output.bpmn', 'main')
        self.workflow = BpmnWorkflow(self.spec)

    def testListWithDictOutput(self):
        self.set_data_and_run_workflow("""input_data = [1, 2, 3]\noutput_data = {}""")
        self.assertDictEqual(self.workflow.data, {'output_data': {0: 2, 1: 4, 2: 6}})

    def testDictWithListOutput(self):
        self.set_data_and_run_workflow("""input_data = {'a': 1, 'b': 2, 'c': 3}\noutput_data = []""")
        self.assertDictEqual(self.workflow.data, {'output_data': [2, 4, 6]})

    def testNonEmptyOutput(self):
        with self.assertRaises(WorkflowDataException) as exc:
            self.set_data_and_run_workflow("""input_data = [1, 2, 3]\noutput_data = [1, 2, 3]""")
            self.assertEqual(exc.exception.message, "If the input is not being updated in place, the output must be empty")

    def testInvalidOutputType(self):
        with self.assertRaises(WorkflowDataException) as exc:
            self.set_data_and_run_workflow("""input_data = set([1, 2, 3])\noutput_data = set([])""")
            self.assertEqual(exc.exception.message, "Only a mutable map (dict) or sequence (list) can be used for output")


class ParallelMultiInstanceNewOutputTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocess = self.load_workflow_spec('parallel_multiinstance_new_output.bpmn', 'main')
        self.workflow = BpmnWorkflow(self.spec)

    def testList(self):
        self.set_data_and_run_workflow("""input_data = [1, 2, 3]""")
        self.assertDictEqual(self.workflow.data, {'output_data': [2, 4, 6]})

    def testDict(self):
        self.set_data_and_run_workflow("""input_data = {'a': 1, 'b': 2, 'c': 3}""")
        self.assertDictEqual(self.workflow.data, {'output_data': {'a': 2, 'b': 4, 'c': 6}})        

    def testSet(self):
        self.set_data_and_run_workflow("""input_data = set([1, 2, 3])""")
        self.assertDictEqual(self.workflow.data, {'output_data': [2, 4, 6]})

    def testEmptyCollection(self):

        set_data = self.workflow.get_tasks_from_spec_name('set_data')[0]
        set_data.task_spec.script = """input_data = []"""
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        self.assertDictEqual(self.workflow.data, {'output_data': []})

    def testCondition(self):

        set_data = self.workflow.get_tasks_from_spec_name('set_data')[0]
        set_data.task_spec.script = """input_data = [1, 2, 3]"""

        task = self.workflow.get_tasks_from_spec_name('any_task')[0]
        task.task_spec.condition = "input_item == 2"
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 3)
        task = [t for t in ready_tasks if t.data['input_item'] == 2][0]
        task.data['output_item'] = task.data['input_item'] * 2
        task.complete()
        self.workflow.do_engine_steps()
        self.workflow.refresh_waiting_tasks()
        self.assertEqual(len([ t for t in ready_tasks if t.state == TaskState.CANCELLED]), 2)
        self.assertTrue(self.workflow.is_completed())
        self.assertDictEqual(self.workflow.data, {'output_data': [4]})


class ParallelMultiInstanceUpdateInputTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocess = self.load_workflow_spec('parallel_multiinstance_update_input.bpmn', 'main')
        self.workflow = BpmnWorkflow(self.spec)

    def testList(self):
        self.set_data_and_run_workflow("""input_data = [1, 2, 3]""")
        self.assertDictEqual(self.workflow.data, {'input_data': [2, 4, 6]})

    def testDict(self):
        self.set_data_and_run_workflow("""input_data = {'a': 1, 'b': 2, 'c': 3}""")
        self.assertDictEqual(self.workflow.data, {'input_data': {'a': 2, 'b': 4, 'c': 6}})


class ParallelMultiInstanceWithCardinality(BaseTestCase):

    def setUp(self) -> None:
        self.spec, subprocess = self.load_workflow_spec('parallel_multiinstance_cardinality.bpmn', 'main')
        self.workflow = BpmnWorkflow(self.spec)

    def testCardinalityWithInputItem(self):
        self.set_data_and_run_workflow("""pass""")
        self.assertDictEqual(self.workflow.data, {'output_data': [0, 2, 4]})

    def testCondition(self):
        task = self.workflow.get_tasks_from_spec_name('any_task')[0]
        task.task_spec.condition = "input_item == 1"

        task = self.workflow.get_tasks_from_spec_name('any_task')[0]
        task.task_spec.condition = "input_item == 2"
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 3)
        task = [t for t in ready_tasks if t.data['input_item'] == 2][0]
        task.data['output_item'] = task.data['input_item'] * 2
        task.complete()
        self.workflow.do_engine_steps()
        self.workflow.refresh_waiting_tasks()
        self.assertEqual(len([ t for t in ready_tasks if t.state == TaskState.CANCELLED]), 2)
        self.assertTrue(self.workflow.is_completed())
        self.assertDictEqual(self.workflow.data, {'output_data': [4]})