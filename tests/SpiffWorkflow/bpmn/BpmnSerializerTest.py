import os
import unittest

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from .BpmnLoaderForTests import TestBpmnParser


class BpmnSerializerTest(unittest.TestCase):
    CORRELATE = BpmnSerializer

    def load_workflow_spec(self, filename, process_name):
        f = os.path.join(os.path.dirname(__file__), 'data', filename)
        parser = TestBpmnParser()
        parser.add_bpmn_files_by_glob(f)
        top_level_spec = parser.get_spec(process_name)
        subprocesses = parser.get_subprocess_specs(process_name)
        return top_level_spec, subprocesses

    def setUp(self):
        super(BpmnSerializerTest, self).setUp()
        self.serializer = BpmnSerializer()
        self.spec, subprocesses = self.load_workflow_spec('random_fact.bpmn', 'random_fact')
        self.workflow = BpmnWorkflow(self.spec, subprocesses)

    def testDeserializeWorkflowSpec(self):
        self.assertIsNotNone(self.spec)

    def testSerializeWorkflowSpec(self):
        spec_serialized = self.serializer.serialize_workflow_spec(self.spec)
        result = self.serializer.deserialize_workflow_spec(spec_serialized)
        spec_serialized2 = self.serializer.serialize_workflow_spec(result)
        self.assertEqual(spec_serialized, spec_serialized2)

    def testSerializeWorkflow(self):
        json = self.serializer.serialize_workflow(self.workflow)
        print(json)

    def testDeserializeWorkflow(self):
        self._compare_with_deserialized_copy(self.workflow)

    def testDeserializeCallActivityChildren(self):
        """Tested as a part of deserialize workflow."""
        pass

    def testSerializeTask(self):
        json = self.serializer.serialize_workflow(self.workflow)
        print(json)

    def testDeserializeTask(self):
        self._compare_with_deserialized_copy(self.workflow)

    def testDeserializeActiveWorkflow(self):
        self.workflow.do_engine_steps()
        self._compare_with_deserialized_copy(self.workflow)

    def testDeserializeWithData(self):
        self.workflow.data["test"] = "my_test"
        json = self.serializer.serialize_workflow(self.workflow)
        wf2 = self.serializer.deserialize_workflow(json, workflow_spec=self.spec)
        self.assertEqual('my_test', wf2.get_data("test"))

    def testDeserializeWithDefaultScriptEngineClass(self):
        json = self.serializer.serialize_workflow(self.workflow)
        wf2 = self.serializer.deserialize_workflow(json, workflow_spec=self.spec)
        self.assertIsNotNone(self.workflow.script_engine)
        self.assertIsNotNone(wf2.script_engine)
        self.assertEqual(self.workflow.script_engine.__class__,
                         wf2.script_engine.__class__)

    @unittest.skip("Deserialize does not persist the script engine, Fix me.")
    def testDeserializeWithCustomScriptEngine(self):
        class CustomScriptEngine(PythonScriptEngine):
            pass

        self.workflow.script_engine = CustomScriptEngine()
        json = self.serializer.serialize_workflow(self.workflow)
        wf2 = self.serializer.deserialize_workflow(json, workflow_spec=self.spec)
        self.assertEqual(self.workflow.script_engine.__class__,
                         wf2.script_engine.__class__)

    def testDeserializeWithDataOnTask(self):
        self.workflow.do_engine_steps()
        user_task = self.workflow.get_ready_user_tasks()[0]
        user_task.data = {"test":"my_test"}
        self._compare_with_deserialized_copy(self.workflow)

    def testLastTaskIsSetAndWorksThroughRestore(self):
        self.workflow.do_engine_steps()
        json = self.serializer.serialize_workflow(self.workflow)
        wf2 = self.serializer.deserialize_workflow(json, workflow_spec=self.spec)
        self.assertIsNotNone(self.workflow.last_task)
        self.assertIsNotNone(wf2.last_task)
        self._compare_workflows(self.workflow, wf2)

    def _compare_with_deserialized_copy(self, wf):
        json = self.serializer.serialize_workflow(wf)
        wf2 = self.serializer.deserialize_workflow(json, workflow_spec=self.spec)
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
    return unittest.TestLoader().loadTestsFromTestCase(BpmnSerializerTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
