import os
import unittest
from io import BytesIO

from SpiffWorkflow.bpmn.serializer.Packager import Packager
from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser

from SpiffWorkflow.camunda.parser.UserTaskParser import UserTaskParser


class PackagerForFormTests(Packager):

    PARSER_CLASS = CamundaParser

    @classmethod
    def package_in_memory(cls, workflow_name, workflow_files, editor='signavio'):
        s = BytesIO()
        p = cls(s, workflow_name, meta_data=[], editor=editor)
        p.add_bpmn_files_by_glob(workflow_files)
        p.create_package()
        return s.getvalue()


class UserTaskParserTest(unittest.TestCase):
    CORRELATE = UserTaskParser

    def load_workflow_spec(self, filename, process_name):
        f = os.path.join(os.path.dirname(__file__), filename)

        return BpmnSerializer().deserialize_workflow_spec(
            PackagerForFormTests.package_in_memory(process_name, f))

    def setUp(self):
        self.spec = self.load_workflow_spec('../data/random_fact.bpmn', 'random_fact')

    def testConstructor(self):
        pass  # this is accomplished through setup.

    def testGetForm(self):
        form = self.spec.task_specs['Task_User_Select_Type'].form
        self.assertIsNotNone(form)

    def testGetEnumField(self):
        form = self.spec.task_specs['Task_User_Select_Type'].form
        self.assertEquals("Fact", form.key)
        self.assertEquals(1, len(form.fields))
        self.assertEquals("type", form.fields[0].id)
        self.assertEquals(3, len(form.fields[0].options))

    def testGetFieldProperties(self):
        form = self.spec.task_specs['Task_User_Select_Type'].form
        self.assertEquals(1, len(form.fields[0].properties))
        self.assertEquals('description', form.fields[0].properties[0].id)
        self.assertEquals('Choose from the list of available types of random facts', form.fields[0].properties[0].value)

    def testGetFieldValidation(self):
        form = self.spec.task_specs['Task_User_Select_Type'].form
        self.assertEquals(1, len(form.fields[0].validation))
        self.assertEquals('maxlength', form.fields[0].validation[0].name)
        self.assertEquals('25', form.fields[0].validation[0].config)

    def testCreateTask(self):
        pass


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(UserTaskParserTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
