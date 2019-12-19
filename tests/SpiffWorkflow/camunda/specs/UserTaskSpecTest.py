import json
import unittest

from SpiffWorkflow.camunda.specs.UserTask import FormField, UserTask, Form, EnumFormField, EnumFormFieldOption
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
        enum_field.add_option('new fool', 'This is new, therefor it is better.')
        self.form.add_field(enum_field)
        self.assertEqual(enum_field, self.user_spec.form.fields[-1])

    def testIsEngineTask(self):
        self.assertFalse(self.user_spec.is_engine_task())




    def test_convert_to_dict(self):
        form = Form()
        field1 = FormField(form_type="text")
        field1.id = "testinput"
        field1.label = "Text Input"
        field1.defaultValue = "noda"
        field2 = EnumFormField()
        field2.id = "color"
        field2.label = "color?"
        field2.add_option("red", "Red")
        field2.add_option("blue", "Blue")
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
        self.assertEquals('{"key": "formKey", '
                          '"fields": ['
                          '{"id": "testinput",'
                          ' "type": "text", '
                          '"label": "Text Input",'
                          ' "defaultValue": "noda"}, '
                          '{"id": "color", '
                          '"type": "enum", '
                          '"label": "color?",'
                          ' "defaultValue": "", '
                          '"options": ['
                          '{"id": "red", "name": "Red"}, '
                          '{"id": "blue", "name": "Blue"}]}]}',
                          json_form)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(UserTaskSpecTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
