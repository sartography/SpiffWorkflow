from ...bpmn.serializer.bpmn_converters import BpmnDataConverter, BpmnTaskSpecConverter

from ..specs.UserTask import UserTask, Form
from ..specs.UserTask import FormField

class UserTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(UserTask, data_converter, typename)
 
    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        dct['form'] = self.form_to_dict(spec.form)
        return dct

    def from_dict(self, dct):
        dct['form'] = Form(init=dct['form'])
        return self.task_spec_from_dict(dct)

    def form_to_dict(self, form):
        dct = {'key': form.key, 'fields': []}
        for field in form.fields:
            new = {
                'id': field.id,
                'default_value': field.default_value,
                'label': field.label,
                'type': field.type,
                'properties': [ prop.__dict__ for prop in field.properties ],
                'validation': [ val.__dict__ for val in field.validation ],
            }
            if field.type == "enum":
                new['options'] = [ opt.__dict__ for opt in field.options ]
            dct['fields'].append(new)
        return dct