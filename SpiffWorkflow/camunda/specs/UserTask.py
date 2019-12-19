# -*- coding: utf-8 -*-
from __future__ import division

from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs import Simple


class UserTask(Simple, BpmnSpecMixin):

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


class FormField:
    def __init__(self, form_type="text"):
        self.id = ""
        self.type = form_type
        self.label = ""
        self.defaultValue = ""

    def jsonable(self):
        return self.__dict__

class EnumFormField(FormField):
    def __init__(self):
        super().__init__("enum")
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


class Form:
    def __init__(self):
        self.key = ""
        self.fields = []

    def add_field(self, field):
        self.fields.append(field)

    def jsonable(self):
        return self.__dict__


