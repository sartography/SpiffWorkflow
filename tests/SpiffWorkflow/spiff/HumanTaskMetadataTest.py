from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from .BaseTestCase import BaseTestCase


class HumanTaskMetadataTest(BaseTestCase):
    def testTaskMetadataValues(self):
        spec, subprocesses = self.load_workflow_spec("human_task_metadata.bpmn", "Process_human_task_metadata")
        workflow = BpmnWorkflow(spec, subprocesses)
        workflow.do_engine_steps()

        task = workflow.get_next_task(state=TaskState.READY)
        self.assertIn("taskMetadataValues", task.task_spec.extensions)
        task_metadata_values = task.task_spec.extensions["taskMetadataValues"]
        self.assertIsInstance(task_metadata_values, dict, "taskMetadataValues should be parsed as a dict, not a string")
        self.assertEqual(task_metadata_values["dynamic_key"], "my_var")
        self.assertEqual(task_metadata_values["static_key"], "'static_value'")

        self.assertIsNone(
            task_metadata_values["key_with_no_value_property_in_xml"], "Metadata value without value attribute should be None"
        )
