import os
import unittest
import json

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnLoaderForTests import TestUserTaskConverter


class BpmnWorkflowSerializerTest(unittest.TestCase):
    """Please note that the BpmnSerializer is Deprecated."""
    SERIALIZER_VERSION = "100.1.ANY"

    def load_workflow_spec(self, filename, process_name):
        f = os.path.join(os.path.dirname(__file__), 'data', filename)
        parser = BpmnParser()
        parser.add_bpmn_files_by_glob(f)
        top_level_spec = parser.get_spec(process_name)
        subprocesses = parser.get_subprocess_specs(process_name)
        return top_level_spec, subprocesses

    def setUp(self):
        super(BpmnWorkflowSerializerTest, self).setUp()
        wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter([TestUserTaskConverter])
        self.serializer = BpmnWorkflowSerializer(wf_spec_converter, version=self.SERIALIZER_VERSION)
        spec, subprocesses = self.load_workflow_spec('random_fact.bpmn', 'random_fact')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testDeserializeWorkflowSpec(self):
        """Tested as a part of deserialize workflow."""
        pass

    def testSerializeWorkflowSpec(self):
        spec_serialized = self.serializer.serialize_json(self.workflow)
        result = self.serializer.deserialize_json(spec_serialized)
        spec_serialized2 = self.serializer.serialize_json(result)
        self.assertEqual(spec_serialized, spec_serialized2)

    def testSerializeWorkflowSpecWithGzip(self):
        spec_serialized = self.serializer.serialize_json(self.workflow, use_gzip=True)
        result = self.serializer.deserialize_json(spec_serialized, use_gzip=True)
        spec_serialized2 = self.serializer.serialize_json(result, use_gzip=True)
        self.assertEqual(spec_serialized, spec_serialized2)

    def testSerlializePerservesVersion(self):
        spec_serialized = self.serializer.serialize_json(self.workflow)
        version = self.serializer.get_version(spec_serialized)
        self.assertEqual(version, self.SERIALIZER_VERSION)

    def testSerializeToOldSerializerThenNewSerializer(self):
        old_serializer = BpmnSerializer()
        old_json = old_serializer.serialize_workflow(self.workflow)
        new_workflow = old_serializer.deserialize_workflow(old_json)
        new_json = self.serializer.serialize_json(new_workflow)
        new_workflow_2 = self.serializer.deserialize_json(new_json)

    def testSerializeWorkflow(self):
        serialized = self.serializer.serialize_json(self.workflow)
        json.loads(serialized)

    def testDeserializeWorkflow(self):
        self._compare_with_deserialized_copy(self.workflow)

    def testDeserializeCallActivityChildren(self):
        """Tested as a part of deserialize workflow."""
        pass

    def testSerializeTask(self):
        self.serializer.serialize_json(self.workflow)

    def testDeserializeTask(self):
        self._compare_with_deserialized_copy(self.workflow)

    def testDeserializeActiveWorkflow(self):
        self.workflow.do_engine_steps()
        self._compare_with_deserialized_copy(self.workflow)

    def testDeserializeWithData(self):
        self.workflow.data["test"] = "my_test"
        json = self.serializer.serialize_json(self.workflow)
        wf2 = self.serializer.deserialize_json(json)
        self.assertEqual('my_test', wf2.get_data("test"))

    def testDeserializeWithDefaultScriptEngineClass(self):
        json = self.serializer.serialize_json(self.workflow)
        wf2 = self.serializer.deserialize_json(json)
        self.assertIsNotNone(self.workflow.script_engine)
        self.assertIsNotNone(wf2.script_engine)
        self.assertEqual(self.workflow.script_engine.__class__,
                         wf2.script_engine.__class__)

    @unittest.skip("Deserialize does not persist the script engine, Fix me.")
    def testDeserializeWithCustomScriptEngine(self):
        class CustomScriptEngine(PythonScriptEngine):
            pass

        self.workflow.script_engine = CustomScriptEngine()
        dct = self.serializer.serialize_json(self.workflow)
        wf2 = self.serializer.deserialize_json(dct)
        self.assertEqual(self.workflow.script_engine.__class__,
                         wf2.script_engine.__class__)

    def testDeserializeWithDataOnTask(self):
        self.workflow.do_engine_steps()
        user_task = self.workflow.get_ready_user_tasks()[0]
        user_task.data = {"test":"my_test"}
        self._compare_with_deserialized_copy(self.workflow)

    def testLastTaskIsSetAndWorksThroughRestore(self):
        self.workflow.do_engine_steps()
        json = self.serializer.serialize_json(self.workflow)
        wf2 = self.serializer.deserialize_json(json)
        self.assertIsNotNone(self.workflow.last_task)
        self.assertIsNotNone(wf2.last_task)
        self._compare_workflows(self.workflow, wf2)

    def test_convert_1_0_to_1_1(self):
        # The serialization used here comes from NestedSubprocessTest saved at line 25 with version 1.0
        fn = os.path.join(os.path.dirname(__file__), 'data', 'serialization', 'v1.0.json')
        wf = self.serializer.deserialize_json(open(fn).read())
        # We should be able to finish the workflow from this point
        ready_tasks = wf.get_tasks(TaskState.READY)
        self.assertEqual('Action3', ready_tasks[0].task_spec.description)
        ready_tasks[0].complete()
        wf.do_engine_steps()
        self.assertEqual(True, wf.is_completed())

    def _compare_with_deserialized_copy(self, wf):
        json = self.serializer.serialize_json(wf)
        wf2 = self.serializer.deserialize_json(json)
        self._compare_workflows(wf, wf2)

    def _compare_workflows(self, w1, w2):
        self.assertIsInstance(w1, BpmnWorkflow)
        self.assertIsInstance(w2, BpmnWorkflow)
        self.assertEqual(w1.data, w2.data)
        self.assertEqual(w1.name, w2.name)
        for task in w1.get_ready_user_tasks():
            w2_task = w2.get_task(task.id)
            self.assertIsNotNone(w2_task)
            self.assertEqual(task.data, w2_task.data)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(BpmnWorkflowSerializerTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
