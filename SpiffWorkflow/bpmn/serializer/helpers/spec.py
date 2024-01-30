# Copyright (C) 2023 Elizabeth Esswein, Sartography
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

from functools import partial

from SpiffWorkflow.operators import Attrib, PathAttrib

from SpiffWorkflow.bpmn.specs.mixins.bpmn_spec_mixin import BpmnSpecMixin
from SpiffWorkflow.bpmn.specs.event_definitions.message import CorrelationProperty
from .bpmn_converter import BpmnConverter


class BpmnDataSpecificationConverter(BpmnConverter):
    """This is the base Data Spec converter.

    This is used for `DataObject` and `TaskDataReference`; it can be extended for other
    types of data specs.
    """

    def to_dict(self, data_spec):
        """Convert a data specification into a dictionary.

        Arguments:
            data_spec (`BpmnDataSpecification): a BPMN data specification

        Returns:
            dict: a dictionary representation of the data spec
        """
        return { 'bpmn_id': data_spec.bpmn_id, 'bpmn_name': data_spec.bpmn_name }

    def from_dict(self, dct):
        """Restores a data specification.

        Arguments:
            dct (dict): the dictionary representation

        Returns:
            an instance of the target class
        """
        return self.target_class(**dct)


class EventDefinitionConverter(BpmnConverter):
    """This is the base Event Defintiion Converter.

    It provides conversions for the great majority of BPMN events as-is, and contains
    one custom method for serializing Correlation Properties (as Message Event Defintiions
    are likely to the most commonly extended event definition spec).
    """

    def to_dict(self, event_definition):
        """Convert an event definition into a dictionary.

        Arguments:
            event_definition: the event definition

        Returns:
            dict: a dictionary representation of the event definition
        """
        dct = {
            'description': event_definition.description,
            'name': event_definition.name
        }
        return dct

    def from_dict(self, dct):
        """Restores an event definition.

        Arguments:
            dct: the dictionary representation

        Returns;
            an instance of the target event definition
        """
        event_definition = self.target_class(**dct)
        return event_definition

    def correlation_properties_to_dict(self, props):
        """Convert correlation properties to a dictionary representation.

        Arguments:
            list(`CorrelationProperty`): the correlation properties associated with a message

        Returns:
            list(dict): a list of dictionary representations of the correlation properties
        """
        return [prop.__dict__ for prop in props]

    def correlation_properties_from_dict(self, props):
        """Restore correlation properties from a dictionary representation

        Arguments:
            props (list(dict)): a list if dictionary representations of correlation properties

        Returns:
            a list of `CorrelationProperty` of a message
        """
        return [CorrelationProperty(**prop) for prop in props]


class TaskSpecConverter(BpmnConverter):
    """Base Task Spec Converter.

    It contains methods for parsing generic and BPMN task spec attributes.

    If you have extended any of the the BPMN tasks with custom functionality, you'll need to
    implement a converter for those task spec types.  You'll need to implement the `to_dict` and
    `from_dict` methods on any inheriting classes.

    The default task spec converters are in the `default.task_spec` modules of this package; the
    `camunda`,`dmn`, and `spiff` serialization packages contain other examples.
    """
    def get_default_attributes(self, spec):
        """Extracts the default BPMN attributes from a task spec.

        Arguments:
            spec: the task spec to be converted

        Returns:
            dict: a dictionary of standard task spec attributes
        """
        return {
            'name': spec.name,
            'description': spec.description,
            'manual': spec.manual,
            'lookahead': spec.lookahead,
            'inputs': spec._inputs,
            'outputs': spec._outputs,
            'bpmn_id': spec.bpmn_id,
            'bpmn_name': spec.bpmn_name,
            'lane': spec.lane,
            'documentation': spec.documentation,
            'data_input_associations': self.registry.convert(spec.data_input_associations),
            'data_output_associations': self.registry.convert(spec.data_output_associations),
            'io_specification': self.registry.convert(spec.io_specification),
        }

    def get_join_attributes(self, spec):
        """Extracts attributes for task specs that inherit from `Join`.

        Arguments:
            spec: the task spec to be converted

        Returns:
            dict: a dictionary of `Join` task spec attributes
        """
        return {
            'split_task': spec.split_task,
            'threshold': spec.threshold,
            'cancel': spec.cancel_remaining,
        }

    def get_subworkflow_attributes(self, spec):
        """Extracts attributes for task specs that inherit from `SubWorkflowTask`.

        Arguments:
            spec: the task spec to be converted

        Returns:
            dict: a dictionary of subworkflow task spec attributes
        """
        return {'spec': spec.spec}

    def get_standard_loop_attributes(self, spec):
        """Extracts attributes for standard loop tasks.

        Arguments:
            spec: the task spec to be converted

        Returns:
            dict: a dictionary of standard loop task spec attributes
        """
        return {
            'task_spec': spec.task_spec,
            'maximum': spec.maximum,
            'condition': spec.condition,
            'test_before': spec.test_before,
        }

    def task_spec_from_dict(self, dct):
        """Creates a task spec based on the supplied dictionary.

        It handles setting the default task spec attributes as well as attributes added by `BpmnSpecMixin`.

        Arguments:
            dct (dict): the dictionary to create the task spec from

        Returns:
            a restored task spec
        """
        dct['data_input_associations'] = self.registry.restore(dct.pop('data_input_associations', []))
        dct['data_output_associations'] = self.registry.restore(dct.pop('data_output_associations', []))
        dct['io_specification'] = self.registry.restore(dct.pop('io_specification', None))

        wf_spec = dct.pop('wf_spec')
        name = dct.pop('name')
        bpmn_id = dct.pop('bpmn_id')

        spec = self.target_class(wf_spec, name, **dct)

        if issubclass(self.target_class, BpmnSpecMixin) and bpmn_id != name:
            # This is a hack for multiinstance tasks :(  At least it is simple.
            # Ideally I'd fix it in the parser, but I'm afraid of quickly running into a wall there
            spec.bpmn_id = bpmn_id

        return spec
