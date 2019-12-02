from SpiffWorkflow.camunda.specs.UserTask import UserTask, Form, FormField, EnumFormField
from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser, xpath_eval


CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'


class UserTaskParser(TaskParser):

    def __init__(self, process_parser, spec_class, node):
        super().__init__(process_parser, spec_class, node)
        self.xpath = xpath_eval(node,extra_ns={'camunda':CAMUNDA_MODEL_NS})
    """
    Base class for parsing User Tasks
    """
    pass

    def create_task(self):
        form = self.get_form()
        return self.spec_class(self.spec, self.get_task_spec_name(), form,
                               description=self.node.get('name', None))

    def get_form(self):
        """Camunda provides a simple form builder, this will extract the
        details from that form and construct a form model from it. """
        form = Form()
        form.key = self.node.attrib['{' + CAMUNDA_MODEL_NS + '}formKey']
        for xml_field in self.xpath('.//camunda:formData/camunda:formField'):
            if xml_field.get('type') == 'enum':
                field = self.get_enum_field(xml_field)
            else:
                field = FormField()
            field.id = xml_field.get('id')
            field.type = xml_field.get('type')
            field.label = xml_field.get('label')
            field.default_value = xml_field.get('defaultValue')
            form.add_field(field)
            print(xml_field.text)
        return form

    def get_enum_field(self, xml_field):
        field = EnumFormField()
        for option in xml_field:
            field.add_option(option.get('id'), option.get('name'))
        return field


