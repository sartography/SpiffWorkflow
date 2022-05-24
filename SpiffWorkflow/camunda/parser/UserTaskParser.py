from ...bpmn.parser.TaskParser import TaskParser
from ...bpmn.parser.util import xpath_eval
from ...camunda.specs.UserTask import Form, FormField, EnumFormField

CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'


class UserTaskParser(TaskParser):
    """
    Base class for parsing User Tasks
    """
    
    def __init__(self, process_parser, spec_class, node, lane=None):
        super(UserTaskParser, self).__init__(process_parser, spec_class, node, lane)
        self.xpath = xpath_eval(node, extra_ns={'camunda': CAMUNDA_MODEL_NS})

    def create_task(self):
        form = self.get_form()
        return self.spec_class(self.spec, self.get_task_spec_name(), form,
                               lane=self.lane,
                               position=self.position,
                               description=self.node.get('name', None))

    def get_form(self):
        """Camunda provides a simple form builder, this will extract the
        details from that form and construct a form model from it. """
        form = Form()
        try:
            form.key = self.node.attrib['{' + CAMUNDA_MODEL_NS + '}formKey']
        except (KeyError):
            return form
        for xml_field in self.xpath('.//camunda:formData/camunda:formField'):
            if xml_field.get('type') == 'enum':
                field = self.get_enum_field(xml_field)
            else:
                field = FormField()

            field.id = xml_field.get('id')
            field.type = xml_field.get('type')
            field.label = xml_field.get('label')
            field.default_value = xml_field.get('defaultValue')

            for child in xml_field:
                if child.tag == '{' + CAMUNDA_MODEL_NS + '}properties':
                    for p in child:
                        field.add_property(p.get('id'), p.get('value'))

                if child.tag == '{' + CAMUNDA_MODEL_NS + '}validation':
                    for v in child:
                        field.add_validation(v.get('name'), v.get('config'))

            form.add_field(field)
        return form

    def get_enum_field(self, xml_field):
        field = EnumFormField()

        for child in xml_field:
            if child.tag == '{' + CAMUNDA_MODEL_NS + '}value':
                field.add_option(child.get('id'), child.get('name'))
        return field
