import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.camunda.serializer.CamundaSerializer import CamundaSerializer


class CamundaSerializerTest(unittest.TestCase):
    CORRELATE = CamundaSerializer

    def setUp(self):
        super(CamundaSerializerTest, self).setUp()
        self.serializer = CamundaSerializer()
        self.spec = self.serializer.deserialize_workflow_spec("../../camunda/data")
        self.workflow = BpmnWorkflow(self.spec)
        self.return_type = str


    def testDeserializeWorkflowSpec(self):
        self.assertIsNotNone(self.spec)

    def testSerializeWorkflowSpec(self):
        with self.assertRaises(NotImplementedError):
            self.serializer.serialize_workflow_spec(self.spec)

    def testSerializeWorkflow(self):
        json = self.serializer.serialize_workflow(self.workflow)
        print(json)

    def testDeserializeWorkflow(self):
        self._compare_with_deserialized_copy(self.workflow)

    def testDeserializeActiveWorkflow(self):
        self.workflow.do_engine_steps()
        self._compare_with_deserialized_copy(self.workflow)

    def testDeserializeWithData(self):
        self.workflow.data["test"] = "my_test"
        json = self.serializer.serialize_workflow(self.workflow)
        wf2 = self.serializer.deserialize_workflow(json, wf_spec=self.spec)
        self.assertEquals('my_test', wf2.get_data("test"))

    def testDeserializeWithDataOnTask(self):
        self.workflow.do_engine_steps()
        user_task = self.workflow.get_ready_user_tasks()[0]
        user_task.data = {"test":"my_test"}
        self._compare_with_deserialized_copy(self.workflow)

    def _compare_with_deserialized_copy(self, wf):
        json = self.serializer.serialize_workflow(wf)
        wf2 = self.serializer.deserialize_workflow(json, wf_spec=self.spec)
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
    return unittest.TestLoader().loadTestsFromTestCase(CamundaSerializerTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
