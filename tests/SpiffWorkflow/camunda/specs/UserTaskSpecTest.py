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

    def test_constructor(self):
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
