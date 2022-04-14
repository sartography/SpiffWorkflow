import os
import unittest

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.camunda.serializer import UserTaskConverter
from SpiffWorkflow.dmn.serializer import BusinessRuleTaskConverter
from tests.SpiffWorkflow.bpmn.BpmnLoaderForTests import TestUserTaskConverter
from tests.SpiffWorkflow.bpmn.PackagerForTests import PackagerForTests



class BpmnWorkflowSerializerTest(unittest.TestCase):
    """Please note that the BpmnSerializer is Deprecated."""
    CORRELATE = BpmnWorkflowSerializer
    SERIALIZER_VERSION = "100.1.ANY"

    def load_workflow_spec(self, filename, process_name):
        f = os.path.join(os.path.dirname(__file__), 'data', filename)

        return BpmnSerializer().deserialize_workflow_spec(
            PackagerForTests.package_in_memory(process_name, f))

    def setUp(self):
        super(BpmnWorkflowSerializerTest, self).setUp()
        wf_spec_converter = \
            BpmnWorkflowSerializer.configure_workflow_spec_converter(
                [UserTaskConverter,
                 BusinessRuleTaskConverter,
                 TestUserTaskConverter])
        self.serializer = \
            BpmnWorkflowSerializer(wf_spec_converter,
                                   version=self.SERIALIZER_VERSION)
        self.spec = self.load_workflow_spec('random_fact.bpmn', 'random_fact')
        self.workflow = BpmnWorkflow(self.spec)
        self.return_type = str

    def testDeserializeWorkflowSpec(self):
        self.assertIsNotNone(self.spec)

    def testSerializeWorkflowSpec(self):
        spec_serialized = self.serializer.serialize_json(self.workflow)
        result = self.serializer.deserialize_json(spec_serialized)
        spec_serialized2 = self.serializer.serialize_json(result)
        self.assertEqual(spec_serialized, spec_serialized2)

    def testSerlializePerservesVersion(self):
        spec_serialized = self.serializer.serialize_json(self.workflow)
        version = self.serializer.get_version(spec_serialized)
        self.assertEqual(version, self.SERIALIZER_VERSION)

    def testSerializeWorkflow(self):
        json = self.serializer.serialize_json(self.workflow)
        print(json)

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
        json = self.serializer.serialize_json(self.workflow)
        wf2 = self.serializer.deserialize_json(json)
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
