from SpiffWorkflow.task import TaskState
from .BaseTestCase import BaseTestCase
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

# Assure we correctly parse and pass on the Spiffworkflow properties in
# an extension.
class SpiffPropertiesTest(BaseTestCase):

    def testTask(self):
        self.task_test()

    def testTaskSaveRestore(self):
        self.task_test(True)

    def task_test(self, save_restore=False):

        spec, subprocesses = self.load_workflow_spec('spiff_properties.bpmn', 'Process_1')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        # The ready task's spec should contain extension properties
        # with name/value pairs.
        task = ready_tasks[0]
        self.assertDictEqual({'formJsonSchemaFilename': 'my_json_jschema.json',
                              'formUiSchemaFilename': 'my_ui_jschema.json'},
        task.task_spec.extensions['properties'])

