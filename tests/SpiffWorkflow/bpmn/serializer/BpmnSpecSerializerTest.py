import json

from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer, BpmnSpecSerializer

from .BaseTestCase import BaseTestCase


class BpmnSpecSerializerTest(BaseTestCase):

    def setUp(self):
        super().setUp()
        registry = BpmnSpecSerializer.configure()
        self.spec_serializer = BpmnSpecSerializer(registry=registry, version=self.SERIALIZER_VERSION)
        canonical_registry = BpmnWorkflowSerializer.configure()
        self.canonical_serializer = BpmnWorkflowSerializer(registry=canonical_registry, version=self.SERIALIZER_VERSION)

    def test_spec_round_trips_to_canonical_dicts(self):
        serialized = self.spec_serializer.serialize_json(self.workflow)
        restored = self.spec_serializer.deserialize_json(serialized)
        canonical = self.canonical_serializer.to_dict(self.workflow)

        self.assertEqual(canonical["spec"], restored["spec"])
        self.assertEqual(canonical["subprocess_specs"], restored["subprocess_specs"])

    def test_spec_json_is_smaller_than_canonical_spec_json(self):
        canonical = self.canonical_serializer.to_dict(self.workflow)
        canonical_spec_json = json.dumps(
            {
                "spec": canonical["spec"],
                "subprocess_specs": canonical["subprocess_specs"],
                "serializer_version": self.SERIALIZER_VERSION,
            }
        )
        compact_spec_json = self.spec_serializer.serialize_json(self.workflow)
        self.assertLess(len(compact_spec_json), len(canonical_spec_json))

    def test_spec_uses_process_table_and_row_encoded_tasks(self):
        payload = json.loads(self.spec_serializer.serialize_json(self.workflow))

        self.assertIn("~pt", payload)
        self.assertIn("~rt", payload)
        self.assertNotIn("~s", payload)
        self.assertNotIn("~ps", payload)

        root_process = payload["~pt"][str(payload["~rt"])]
        self.assertIsInstance(root_process, list)
        self.assertIsInstance(root_process[1], list)
        self.assertTrue(root_process[1])
        self.assertIsInstance(root_process[1][0], list)
