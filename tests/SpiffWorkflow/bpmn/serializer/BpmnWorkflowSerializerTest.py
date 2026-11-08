# Copyright (C) 2026 omrzk

import unittest
import os
import json

from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.serializer.config import DEFAULT_CONFIG
from SpiffWorkflow.bpmn.serializer.default.workflow import SimpleTaskConverter
from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine
from SpiffWorkflow.task import Task

from .BaseTestCase import BaseTestCase

class BpmnWorkflowSerializerTest(BaseTestCase):

    SERIALIZER_VERSION = "100.1.ANY"
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

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
        a_task = self.workflow.get_tasks(spec_name=a_task_spec.name)[0]
        a_task.data['jsonTest'] = unserializable

        try:
            self.assertRaises(TypeError, self.serializer.serialize_json, self.workflow)
            wf_spec_converter = BpmnWorkflowSerializer.configure()
            custom_serializer = BpmnWorkflowSerializer(wf_spec_converter,
                                                       version=self.SERIALIZER_VERSION,
                                                       json_encoder_cls=MyJsonEncoder,
                                                       json_decoder_cls=MyJsonDecoder)
            serialized_workflow = custom_serializer.serialize_json(self.workflow)
        finally:
            a_task.data.pop('jsonTest',None)

        serialized_task = [x for x in json.loads(serialized_workflow)['tasks'].values() if x['task_spec'] == a_task_spec.name][0]
        self.assertEqual(serialized_task['data']['jsonTest'], {'a': 1, 'my_type': 'mycls'})

        deserialized_workflow = custom_serializer.deserialize_json(serialized_workflow)
        deserialized_task = deserialized_workflow.get_tasks(spec_name=a_task_spec.name)[0]
        self.assertTrue(isinstance(deserialized_task.data['jsonTest'], MyCls))

    def testDeserializeWorkflow(self):
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
        user_task = self.get_ready_user_tasks()[0]
        user_task.data = {"test":"my_test"}
        self._compare_with_deserialized_copy(self.workflow)

    def testDeserializeReorderedTasks(self):
        self.workflow.task_tree.set_data(inherited={'value': 1}, removed=True)
        self.workflow.do_engine_steps()
        user_task = self.get_ready_user_tasks()[0]
        user_task.data['inherited']['value'] = 2
        del user_task.data['removed']
        user_task.set_data(amount=100)
        user_task.run()
        self.workflow.do_engine_steps()
        self._compare_reordered_workflows(self.workflow)

    def testDeserializeReorderedSubprocessTasks(self):
        spec, subprocesses = self.load_workflow_spec('call_activity_*.bpmn', 'Process_8200379')
        workflow = BpmnWorkflow(spec, subprocesses)
        workflow.do_engine_steps()
        self.assertTrue(workflow.completed)
        self._compare_reordered_workflows(workflow)

    def testDeserializeReorderedFullTaskRecords(self):
        config = dict(DEFAULT_CONFIG)
        config[Task] = SimpleTaskConverter
        registry = BpmnWorkflowSerializer.configure(config)
        self.serializer = BpmnWorkflowSerializer(registry, version=self.SERIALIZER_VERSION)
        self.workflow.task_tree.set_data(inherited={'value': 1})
        self.workflow.do_engine_steps()
        self._compare_reordered_workflows(self.workflow)

    def _compare_reordered_workflows(self, workflow):
        serialized = self.serializer.to_dict(workflow)
        for order in ('original', 'reversed', 'sorted'):
            with self.subTest(order=order):
                dct = json.loads(json.dumps(serialized))
                for wf in [dct] + list(dct['subprocesses'].values()):
                    keys = list(wf['tasks'])
                    if order == 'reversed':
                        keys.reverse()
                    elif order == 'sorted':
                        keys.sort()
                    wf['tasks'] = {key: wf['tasks'][key] for key in keys}
                restored = self.serializer.from_dict(dct)
                self._compare_workflows(workflow, restored)
                for task_id, subprocess in workflow.subprocesses.items():
                    restored_subprocess = restored.subprocesses[task_id]
                    self.assertEqual(subprocess.data, restored_subprocess.data)
                    for child_id, task in subprocess.tasks.items():
                        self.assertEqual(task.data, restored_subprocess.tasks[child_id].data)

    def testSerializeIgnoresCallable(self):
        self.workflow.do_engine_steps()
        user_task = self.get_ready_user_tasks()[0]
        def f(n):
            return n + 1
        user_task.data = { 'f': f }
        task_id = str(user_task.id)
        dct = self.serializer.to_dict(self.workflow)
        self.assertNotIn('f', dct['tasks'][task_id]['data'])

    def testLastTaskIsSetAndWorksThroughRestore(self):
        self.workflow.do_engine_steps()
        json = self.serializer.serialize_json(self.workflow)
        wf2 = self.serializer.deserialize_json(json)
        self.assertIsNotNone(self.workflow.last_task)
        self.assertIsNotNone(wf2.last_task)
        self._compare_workflows(self.workflow, wf2)

    def test_serialize_workflow_where_script_task_includes_function(self):
        self.workflow.do_engine_steps()
        ready_tasks = self.get_ready_user_tasks()
        ready_tasks[0].run()
        self.workflow.do_engine_steps()
        self.serializer.serialize_json(self.workflow)
        assert self.workflow.completed
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

        for task in w1.get_tasks():
            w2_task = w2.get_task_from_id(task.id)
            self.assertIsNotNone(w2_task)
            self.assertEqual(task.data, w2_task.data)
