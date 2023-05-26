from .BaseTestCase import BaseTestCase
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

# Assure we correctly parse and pass on the Spiffworkflow properties in
# an extension.
class ScriptUnitTestExtensionsTest(BaseTestCase):

    def testTask(self):
        self.task_test()

    def testTaskSaveRestore(self):
        self.task_test(True)

    def task_test(self, save_restore=False):

        spec, subprocesses = self.load_workflow_spec('script_task_with_unit_tests.bpmn',
                                                     'Process_ScriptTaskWithUnitTests')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()

        # unitTests should be a list of dicts
        expected_unit_tests_wrapper_class = list
        expected_unit_test_class = dict

        script_with_unit_tests = [t for t in self.workflow.get_tasks() if
                t.task_spec.name == 'script_with_unit_test_id'][0]

        extensions = script_with_unit_tests.task_spec.extensions
        unit_test_extensions = extensions['unitTests']

        self.assertEqual(len(unit_test_extensions), 2)
        self.assertIsInstance(unit_test_extensions, expected_unit_tests_wrapper_class)

        first_unit_test = unit_test_extensions[0]
        self.assertIsInstance(first_unit_test, expected_unit_test_class)

        expected_first_unit_test = {
            'id': 'sets_hey_to_true_if_hey_is_false',
            'inputJson': '{"hey": false}', 'expectedOutputJson': '{"hey": true}'
        }
        self.assertDictEqual(first_unit_test, expected_first_unit_test)
