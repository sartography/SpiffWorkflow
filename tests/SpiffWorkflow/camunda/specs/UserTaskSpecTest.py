import json
import unittest

from SpiffWorkflow.camunda.specs.UserTask import FormField, UserTask, Form, \
    EnumFormField
from SpiffWorkflow.specs import WorkflowSpec, TaskSpec


class UserTaskSpecTest(unittest.TestCase):
    CORRELATE = UserTask

    def create_instance(self):
        if 'testtask' in self.wf_spec.task_specs:
            del self.wf_spec.task_specs['testtask']
        task_spec = TaskSpec(self.wf_spec, 'testtask', description='foo')
        self.form = Form()
        return UserTask(self.wf_spec, 'userTask', self.form)

    def setUp(self):
        self.wf_spec = WorkflowSpec()
        self.user_spec = self.create_instance()

    def testConstructor(self):
        self.assertEquals(self.user_spec.name, 'userTask')
        self.assertEqual(self.user_spec.data, {})
        self.assertEqual(self.user_spec.defines, {})
        self.assertEqual(self.user_spec.pre_assign, [])
        self.assertEqual(self.user_spec.post_assign, [])
        self.assertEqual(self.user_spec.locks, [])

    def test_set_form(self):
        self.assertEqual(self.form, self.user_spec.form)

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
        self.assertEquals("flintstone", form_field.get_property("wilma"))


    def testIsEngineTask(self):
        self.assertFalse(self.user_spec.is_engine_task())

    def test_convert_to_dict(self):
        form = Form()

        field1 = FormField(form_type="text")
        field1.id = "quest"
        field1.label = "What is your quest?"
        field1.defaultValue = "I seek the grail!"

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

        form.key = "formKey"
        form.add_field(field1)
        form.add_field(field2)

        def JsonableHandler(Obj):
            if hasattr(Obj, 'jsonable'):
                return Obj.jsonable()
            else:
                raise 'Object of type %s with value of %s is not JSON serializable' % (
                    type(Obj), repr(Obj))

        json_form = json.dumps(form, default=JsonableHandler)
        actual = json.loads(json_form)

        expected = {
            "fields": [
                {
                    "defaultValue": "I seek the grail!",
                    "label": "What is your quest?",
                    "id": "quest",
                    "properties": [],
                    "type": "text",
                    "validation": [],
                },
                {
                    "defaultValue": "",
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
        }

        expected_parsed = json.loads(json.dumps(expected))

        self.maxDiff = None
        self.assertDictEqual(actual, expected_parsed)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(UserTaskSpecTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
