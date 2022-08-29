# -*- coding: utf-8 -*-


from ...bpmn.specs.UserTask import UserTask
from ...bpmn.specs.BpmnSpecMixin import BpmnSpecMixin


class UserTask(UserTask, BpmnSpecMixin):

    def __init__(self, wf_spec, name, form, **kwargs):
        """
        Constructor.
        :param form: the information that needs to be provided by the user,
        as parsed from the camunda xml file's form details.
        """
        super(UserTask, self).__init__(wf_spec, name, **kwargs)
        self.form = form


    """
    Task Spec for a bpmn:userTask node.
    """

    def _on_trigger(self, my_task):
        pass

    def is_engine_task(self):
        return False

    def serialize(self, serializer):
        return serializer.serialize_user_task(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_user_task(wf_spec, s_state)


class FormField(object):
    def __init__(self, form_type="text"):
        self.id = ""
        self.type = form_type
        self.label = ""
        self.default_value = ""
        self.properties = []
        self.validation = []

    def add_property(self, property_id, value):
        self.properties.append(FormFieldProperty(property_id, value))

    def add_validation(self, name, config):
        self.validation.append(FormFieldValidation(name, config))

    def get_property(self, property_id):
        for prop in self.properties:
            if prop.id == property_id:
                return prop.value

    def has_property(self, property_id):
        return self.get_property(property_id) is not None

    def get_validation(self, name):
        for v in self.validation:
            if v.name == name:
                return v.config

    def has_validation(self, name):
        return self.get_validation(name) is not None

    def jsonable(self):
        return self.__dict__

class EnumFormField(FormField):
    def __init__(self):
        super(EnumFormField, self).__init__("enum")
        self.options = []

    def add_option(self, option_id, name):
        self.options.append(EnumFormFieldOption(option_id, name))

    def jsonable(self):
        return self.__dict__


class EnumFormFieldOption:
    def __init__(self, option_id, name):
        self.id = option_id
        self.name = name

    def jsonable(self):
        return self.__dict__


class FormFieldProperty:
    def __init__(self, property_id, value):
        self.id = property_id
        self.value = value

    def jsonable(self):
        return self.__dict__


class FormFieldValidation:
    def __init__(self, name, config):
        self.name = name
        self.config = config

    def jsonable(self):
        return self.__dict__


class Form:
    def __init__(self,init=None):
        self.key = ""
        self.fields = []
        if init:
            self.from_dict(init)

    def add_field(self, field):
        self.fields.append(field)

    def jsonable(self):
        return self.__dict__

    def from_dict(self,formdict):
        self.key = formdict['key']
        for field in formdict['fields']:
            if field['type'] == 'enum':
                newfield = EnumFormField()
                for option in field['options']:
                    newfield.add_option(option['id'], option['name'])
            else:
                newfield = FormField()
            newfield.id = field['id']
            newfield.default_value = field['default_value']
            newfield.label = field['label']
            newfield.type = field['type']
            for prop in field['properties']:
                newfield.add_property(prop['id'],prop['value'])
            for validation in field['validation']:
                newfield.add_validation(validation['name'],validation['config'])
            self.add_field(newfield)


