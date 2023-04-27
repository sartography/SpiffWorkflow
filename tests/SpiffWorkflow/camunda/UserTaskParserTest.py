import unittest

from SpiffWorkflow.camunda.parser.task_spec import UserTaskParser
from tests.SpiffWorkflow.camunda.BaseTestCase import BaseTestCase


class UserTaskParserTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocesses = self.load_workflow_spec('random_fact.bpmn', 'random_fact')

    def testGetForm(self):
        form = self.spec.task_specs['Task_User_Select_Type'].form
        self.assertIsNotNone(form)

    def testGetEnumField(self):
        form = self.spec.task_specs['Task_User_Select_Type'].form
        self.assertEqual("Fact", form.key)
        self.assertEqual(1, len(form.fields))
        self.assertEqual("type", form.fields[0].id)
        self.assertEqual(3, len(form.fields[0].options))

    def testGetFieldProperties(self):
        form = self.spec.task_specs['Task_User_Select_Type'].form
        self.assertEqual(1, len(form.fields[0].properties))
        self.assertEqual('description', form.fields[0].properties[0].id)
        self.assertEqual('Choose from the list of available types of random facts', form.fields[0].properties[0].value)

    def testGetFieldValidation(self):
        form = self.spec.task_specs['Task_User_Select_Type'].form
        self.assertEqual(1, len(form.fields[0].validation))
        self.assertEqual('maxlength', form.fields[0].validation[0].name)
        self.assertEqual('25', form.fields[0].validation[0].config)

    def testNoFormDoesNotBombOut(self):
        self.load_workflow_spec('no_form.bpmn', 'no_form')
        self.assertTrue(True) # You can load a user task that has no form and you can still get here.

    def testCreateTask(self):
        pass


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(UserTaskParserTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
