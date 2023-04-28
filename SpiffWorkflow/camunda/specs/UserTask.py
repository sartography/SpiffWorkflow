# Copyright (C) 2023 Sartography
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

from ...bpmn.specs.UserTask import UserTask as DefaultUserTask


class UserTask(DefaultUserTask):
    """Task Spec for a bpmn:userTask node with Camunda forms."""

    def __init__(self, wf_spec, name, form, **kwargs):
        """
        Constructor.
        :param form: the information that needs to be provided by the user,
        as parsed from the camunda xml file's form details.
        """
        super(UserTask, self).__init__(wf_spec, name, **kwargs)
        self.form = form


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


class EnumFormField(FormField):
    def __init__(self):
        super(EnumFormField, self).__init__("enum")
        self.options = []

    def add_option(self, option_id, name):
        self.options.append(EnumFormFieldOption(option_id, name))


class EnumFormFieldOption:
    def __init__(self, option_id, name):
        self.id = option_id
        self.name = name



class FormFieldProperty:
    def __init__(self, property_id, value):
        self.id = property_id
        self.value = value


class FormFieldValidation:
    def __init__(self, name, config):
        self.name = name
        self.config = config


class Form:
    def __init__(self,init=None):
        self.key = ""
        self.fields = []
        if init:
            self.from_dict(init)

    def add_field(self, field):
        self.fields.append(field)

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


