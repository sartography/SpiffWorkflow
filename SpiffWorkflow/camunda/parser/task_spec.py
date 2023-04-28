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

from ...camunda.specs.UserTask import Form, FormField, EnumFormField

from SpiffWorkflow.bpmn.specs.data_spec import TaskDataReference
from SpiffWorkflow.bpmn.parser.util import one
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser
from SpiffWorkflow.bpmn.parser.task_parsers import SubprocessParser

from SpiffWorkflow.dmn.specs.BusinessRuleTask import BusinessRuleTask

from SpiffWorkflow.camunda.specs.multiinstance_task import SequentialMultiInstanceTask, ParallelMultiInstanceTask

CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'


class CamundaTaskParser(TaskParser):

    def parse_extensions(self, node=None):
        extensions = {}
        extension_nodes = self.xpath('.//bpmn:extensionElements/camunda:properties/camunda:property')
        for ex_node in extension_nodes:
            extensions[ex_node.get('name')] = ex_node.get('value')
        return extensions

    def _add_multiinstance_task(self, loop_characteristics):

        sequential = loop_characteristics.get('isSequential') == 'true'
        prefix = 'bpmn:multiInstanceLoopCharacteristics'

        cardinality = self.xpath(f'./{prefix}/bpmn:loopCardinality')
        cardinality = cardinality[0].text if len(cardinality) > 0 else None
        collection = self.attribute('collection', 'camunda', loop_characteristics)
        if cardinality is None and collection is None:
            self.raise_validation_exception('A multiinstance task must specify a cardinality or a collection')

        element_var = self.attribute('elementVariable', 'camunda', loop_characteristics)
        condition = self.xpath(f'./{prefix}/bpmn:completionCondition')
        condition = condition[0].text if len(condition) > 0 else None

        original = self.spec.task_specs.pop(self.task.name)

        # We won't include the data input, because sometimes it is the collection, and other times it
        # is the cardinality.  The old MI task evaluated the cardinality at run time and treated it like
        # a cardinality if it evaluated to an int, and as the data input if if evaluated to a collection
        # I highly doubt that this is the way Camunda worked then, and I know that's not how it works
        # now, and I think we should ultimately replace this with something that corresponds to how
        # Camunda actually handles things; however, for the time being, I am just going to try to 
        # replicate the old behavior as closely as possible.
        # In our subclassed MI task, we'll update the BPMN multiinstance attributes when the task starts.
        params = {
            'task_spec': '',
            'cardinality': cardinality, 
            'data_output': TaskDataReference(collection) if collection is not None else None,
            'output_item': TaskDataReference(element_var) if element_var is not None else None,
            'condition': condition,
        }
        if sequential:
            self.task = SequentialMultiInstanceTask(self.spec, original.name, **params)
        else:
            self.task = ParallelMultiInstanceTask(self.spec, original.name, **params)
        self._copy_task_attrs(original)


class BusinessRuleTaskParser(CamundaTaskParser):
    dmn_debug = None

    def create_task(self):
        decision_ref = self.get_decision_ref(self.node)
        return BusinessRuleTask(self.spec, self.get_task_spec_name(),
                                dmnEngine=self.process_parser.parser.get_engine(decision_ref, self.node),
                                lane=self.lane, position=self.position,
                                description=self.node.get('name', None),
                                )

    @staticmethod
    def get_decision_ref(node):
        return node.attrib['{' + CAMUNDA_MODEL_NS + '}decisionRef']


class UserTaskParser(CamundaTaskParser):
    """Base class for parsing User Tasks"""

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
            form.key = self.attribute('formKey', 'camunda')
        except KeyError:
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

            prefix = '{' + self.nsmap.get('camunda') + '}'
            for child in xml_field:
                if child.tag == f'{prefix}properties':
                    for p in child:
                        field.add_property(p.get('id'), p.get('value'))

                if child.tag == f'{prefix}validation':
                    for v in child:
                        field.add_validation(v.get('name'), v.get('config'))

            form.add_field(field)
        return form

    def get_enum_field(self, xml_field):
        field = EnumFormField()

        for child in xml_field:
            if child.tag == '{' + self.nsmap.get('camunda') + '}value':
                field.add_option(child.get('id'), child.get('name'))
        return field


# These classes need to be able to use the overriden _add_multiinstance_task method
# so they have to inherit from CamundaTaskParser.  Therefore, the parsers have to just
# be copied, because both they and the CamundaTaskParser inherit from the base task
# parser.  I am looking forward to the day when I can replaced all of this with
# something sane and sensible.

class SubWorkflowParser(CamundaTaskParser):

    def create_task(self):
        subworkflow_spec = SubprocessParser.get_subprocess_spec(self)
        return self.spec_class(
            self.spec, self.get_task_spec_name(), subworkflow_spec,
            lane=self.lane, position=self.position,
            description=self.node.get('name', None))


class CallActivityParser(CamundaTaskParser):
    """Parses a CallActivity node."""

    def create_task(self):
        subworkflow_spec = SubprocessParser.get_call_activity_spec(self)
        return self.spec_class(
            self.spec, self.get_task_spec_name(), subworkflow_spec,
            lane=self.lane, position=self.position,
            description=self.node.get('name', None))


class ScriptTaskParser(TaskParser):
    """
    Parses a script task
    """

    def create_task(self):
        script = self.get_script()
        return self.spec_class(self.spec, self.get_task_spec_name(), script,
                               lane=self.lane,
                               position=self.position,
                               description=self.node.get('name', None))

    def get_script(self):
        """
        Gets the script content from the node. A subclass can override this
        method, if the script needs to be pre-parsed. The result of this call
        will be passed to the Script Engine for execution.
        """
        try:
            return one(self.xpath('.//bpmn:script')).text
        except AssertionError as ae:
            raise ValidationException(
                f"Invalid Script Task.  No Script Provided. " + str(ae),
                node=self.node, file_name=self.filename)
