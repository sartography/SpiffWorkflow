import unittest

from SpiffWorkflow.camunda.parser.UserTaskParser import UserTaskParser
from SpiffWorkflow.camunda.serializer.CamundaSerializer import CamundaSerializer


class UserTaskParserTest(unittest.TestCase):
    CORRELATE = UserTaskParser

    def test_deserialize_bpmn_finds_camunda_form_with_options(self):
        serializer = CamundaSerializer()
        spec = serializer.deserialize_workflow_spec("../data")
        form = spec.task_specs['Task_User_Select_Type'].form
        self.assertIsNotNone(form)
        self.assertEquals("Fact", form.key)
        self.assertEquals(1, len(form.fields))
        self.assertEquals("type", form.fields[0].id)
        self.assertEquals(3, len(form.fields[0].options))
