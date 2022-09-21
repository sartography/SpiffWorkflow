import os
import unittest
import json
from uuid import uuid4

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

    def testSerializeWorkflowCustomJSONEncoderDecoder(self):
        class MyCls:
            a = 1
            def to_dict(self):
                return {'a': 1, 'my_type': 'mycls'}

            @classmethod
            def from_dict(self, data):
                return MyCls()

        class MyJsonEncoder(json.JSONEncoder):
            def default(self, z):
                if isinstance(z, MyCls):
                    return z.to_dict()
                return super().default(z)

        class MyJsonDecoder(json.JSONDecoder):
            classes = {'mycls': MyCls}

            def __init__(self, *args, **kwargs):
                super().__init__(object_hook=self.object_hook, *args, **kwargs)

            def object_hook(self, z):
                if 'my_type' in z and z['my_type'] in self.classes:
                    return self.classes[z['my_type']].from_dict(z)

                return z

        unserializable = MyCls()

        a_task_spec = self.workflow.spec.task_specs[list(self.workflow.spec.task_specs)[0]]
        a_task = self.workflow.get_tasks_from_spec_name(a_task_spec.name)[0]
        a_task.data['jsonTest'] = unserializable

        try:
            self.assertRaises(TypeError, self.serializer.serialize_json, self.workflow)
            wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter([TestUserTaskConverter])
            custom_serializer = BpmnWorkflowSerializer(wf_spec_converter, version=self.SERIALIZER_VERSION,json_encoder_cls=MyJsonEncoder, json_decoder_cls=MyJsonDecoder)
            serialized_workflow = custom_serializer.serialize_json(self.workflow)
        finally:
            a_task.data.pop('jsonTest',None)

        serialized_task = [x for x in json.loads(serialized_workflow)['tasks'].values() if x['task_spec'] == a_task_spec.name][0]
        self.assertEqual(serialized_task['data']['jsonTest'], {'a': 1, 'my_type': 'mycls'})

        deserialized_workflow = custom_serializer.deserialize_json(serialized_workflow)
        deserialized_task = deserialized_workflow.get_tasks_from_spec_name(a_task_spec.name)[0]
        self.assertTrue(isinstance(deserialized_task.data['jsonTest'], MyCls))

    def testDeserializeWorkflow(self):
        self._compare_with_deserialized_copy(self.workflow)

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

    def testSerializeIgnoresCallable(self):
        self.workflow.do_engine_steps()
        user_task = self.workflow.get_ready_user_tasks()[0]
        def f(n):
            return n + 1
        user_task.data = { 'f': f }
        task_id = str(user_task.id)
        dct = self.serializer.workflow_to_dict(self.workflow)
        self.assertNotIn('f', dct['tasks'][task_id]['data'])

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

    def test_serialize_workflow_where_script_task_includes_function(self):
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_ready_user_tasks()
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()
        results = self.serializer.serialize_json(self.workflow)
        assert self.workflow.is_completed()
        assert 'y' in self.workflow.last_task.data
        assert 'x' not in self.workflow.last_task.data
        assert 'some_fun' not in self.workflow.last_task.data

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
