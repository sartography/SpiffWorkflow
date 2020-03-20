import unittest

from SpiffWorkflow.camunda.parser.UserTaskParser import UserTaskParser
from tests.SpiffWorkflow.camunda.BaseTest import BaseTest


class UserTaskParserTest(BaseTest):
    CORRELATE = UserTaskParser

    def setUp(self):
        self.spec = self.load_workflow_spec('data/random_fact.bpmn', 'random_fact')

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

    def testNoFormDoesNotBombOut(self):
        self.load_workflow_spec('data/no_form.bpmn', 'no_form')
        self.assertTrue(True) # You can load a user task that has no form and you can still get here.

    def testCreateTask(self):
        pass


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(UserTaskParserTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
