import unittest

from SpiffWorkflow.camunda.specs.user_task import FormField, UserTask, Form, EnumFormField
from SpiffWorkflow.camunda.serializer.task_spec import UserTaskConverter
from SpiffWorkflow.bpmn.serializer.helpers.dictionary import DictionaryConverter
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec


class UserTaskSpecTest(unittest.TestCase):

    def create_instance(self):
        if 'testtask' in self.wf_spec.task_specs:
            del self.wf_spec.task_specs['testtask']
        self.form = Form()
        return UserTask(self.wf_spec, 'userTask', self.form)

    def setUp(self):
        self.wf_spec = WorkflowSpec()
        self.user_spec = self.create_instance()

    def testConstructor(self):
        self.assertEqual(self.user_spec.name, 'userTask')
        self.assertEqual(self.user_spec.data, {})
        self.assertEqual(self.user_spec.defines, {})
        self.assertEqual(self.user_spec.pre_assign, [])
        self.assertEqual(self.user_spec.post_assign, [])

    def test_set_form(self):
        self.assertEqual(self.form, self.user_spec.form)

    def testSerialize(self):
        field1 = FormField(form_type="text")
        field1.id = "quest"
        field1.label = "What is your quest?"
        field1.default_value = "I seek the grail!"

        field2 = EnumFormField()
        field2.id = "color"
        field2.label = "What is your favorite color?"
        field2.add_option("red", "Red")
        field2.add_option("orange", "Green")
        field2.add_option("yellow", "Yellow")
        field2.add_option("green", "Green")
        field2.add_option("blue", "Blue")
        field2.add_option("indigo", "Indigo")
        field2.add_option("violet", "Violet")
        field2.add_option("other", "Other")
        field2.add_property("description", "You know what to do.")
        field2.add_validation("maxlength", "25")

        self.form.key = "formKey"
        self.form.add_field(field1)
        self.form.add_field(field2)

        converter = UserTaskConverter(UserTask, DictionaryConverter())
        dct = converter.to_dict(self.user_spec)
        self.assertEqual(dct['name'], 'userTask')
        self.assertEqual(dct['form'], {
            "fields": [
                {
                    "default_value": "I seek the grail!",
                    "label": "What is your quest?",
                    "id": "quest",
                    "properties": [],
                    "type": "text",
                    "validation": [],
                },
                {
                    "default_value": "",
                    "id": "color",
                    "label": "What is your favorite color?",
                    "options": [
                        {"id": "red", "name": "Red"},
                        {"id": "orange", "name": "Green"},
                        {"id": "yellow", "name": "Yellow"},
                        {"id": "green", "name": "Green"},
                        {"id": "blue", "name": "Blue"},
                        {"id": "indigo", "name": "Indigo"},
                        {"id": "violet", "name": "Violet"},
                        {"id": "other", "name": "Other"},
                    ],
                    "properties": [
                        {"id": "description", "value": "You know what to do."},
                    ],
                    "type": "enum",
                    "validation": [
                        {"name": "maxlength", "config": "25"},
                    ],
                }
            ],
            "key": "formKey",
        })

    def test_text_field(self):
        form_field = FormField(form_type="text")
        form_field.id = "1234"
        self.form.add_field(form_field)
        self.assertEqual(form_field, self.user_spec.form.fields[0])

    def test_enum_field(self):
        enum_field = EnumFormField()
        enum_field.label = "Which kind of fool are you"
        enum_field.add_option('old fool', 'This is old, therefor it is good.')
        enum_field.add_option('new fool',
                              'This is new, therefor it is better.')
        self.form.add_field(enum_field)
        self.assertEqual(enum_field, self.user_spec.form.fields[-1])

    def test_properties(self):
        form_field = FormField(form_type="text")
        self.assertFalse(form_field.has_property("wilma"))
        form_field.add_property("wilma", "flintstone")
        self.assertTrue(form_field.has_property("wilma"))
        self.assertEqual("flintstone", form_field.get_property("wilma"))

    def test_validations(self):
        form_field = FormField(form_type="text")
        self.assertFalse(form_field.has_validation("barney"))
        form_field.add_validation("barney", "rubble")
        self.assertTrue(form_field.has_validation("barney"))
        self.assertEqual("rubble", form_field.get_validation("barney"))

    def testIsEngineTask(self):
        self.assertTrue(self.user_spec.manual)
