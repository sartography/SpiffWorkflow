import unittest

from SpiffWorkflow.camunda.serializer.CamundaSerializer import CamundaSerializer


class CamundaSerializerTest(unittest.TestCase):
    CORRELATE = CamundaSerializer

    def setUp(self):
        self.serializer = CamundaSerializer()
        self.spec = self.serializer.deserialize_workflow_spec("./camunda/data")

    def testDeserializeWorkflowSpec(self):
        self.assertIsNotNone(self.spec)

    def testSerializeWorkflowSpec(self):
        with self.assertRaises(NotImplementedError):
            self.serializer.serialize_workflow_spec(self.spec)

    def testSerializeWorkflow(self):
        with self.assertRaises(NotImplementedError):
            self.serializer.serialize_workflow(self.spec)

    def testDeserializeWorkflow(self):
        with self.assertRaises(NotImplementedError):
            self.serializer.deserialize_workflow(self.spec)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CamundaSerializerTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
