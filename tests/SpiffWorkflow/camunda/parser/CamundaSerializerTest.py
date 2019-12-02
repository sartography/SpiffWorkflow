import unittest

from SpiffWorkflow.camunda.serializer.CamundaSerializer import CamundaSerializer


class CamundaSerializerTest(unittest.TestCase):
    CORRELATE = CamundaSerializer

    def setUp(self):
        self.serializer = CamundaSerializer()
        self.spec = self.serializer.deserialize_workflow_spec("../data")

    def test_deserialize_workflow_spec(self):
        self.assertIsNotNone(self.spec)

    def test_serialize_workflow_spec(self):
        with self.assertRaises(NotImplementedError):
            self.serializer.serialize_workflow_spec(self.spec)

    def test_serialize_workflow(self):
        with self.assertRaises(NotImplementedError):
            self.serializer.serialize_workflow(self.spec)

    def test_deserialize_workflow(self):
        with self.assertRaises(NotImplementedError):
            self.serializer.deserialize_workflow(self.spec)

