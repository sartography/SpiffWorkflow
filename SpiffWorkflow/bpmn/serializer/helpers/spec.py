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


class BpmnSpecConverter:
    """The base class for conversion of BPMN spec classes.

    In general, most classes that extend this would simply take an existing registry as an
    argument and automatically supply the class along with the implementations of the
    conversion functions `to_dict` and `from_dict`.

    The operation of the spec converter is a little opaque, but hopefully makes sense with a
    little explanation.

    The registry is a `DictionaryConverter` that registers conversion methods by class.  It can be
    pre-populated with methods for custom data (though this is not required) and is passed into
    each of these sublclasses.  When a subclass of this one gets instantiated, it adds itself 
    to this registry.  
    
    This seems a little bit backwards -- the registry is using the subclass, so it seems like we 
    ought to pass the subclass to the registry.  However, there is a lot of interdependence across 
    the spec classes, so this doesn't work that well in practice -- most classes need to know about
    all the other classes, and this was the most concise way I could think of to make that happen.

    The goal is to be able to replace almost any spec class at the top level without classes that 
    use it to reimplement conversion mechanisms.  So for example, it is not necessary to 
    re-implemnent all event-based task spec conversions because, eg, the
    `MessageEventDefintion` was modified.
    """
    def __init__(self, spec_class, registry, typename=None):
        """Constructor for a BPMN spec.

        :param spec_class: the class of the spec the subclass provides conversions for
        :param registry: a registry of conversions to which this one should be added
        :param typename: the name of the class as it will appear in the serialization
        """
        self.spec_class = spec_class
        self.registry = registry
        self.typename = typename if typename is not None else spec_class.__name__     
        self.registry.register(spec_class, self.to_dict, self.from_dict, self.typename)   

    def to_dict(self, spec):
        raise NotImplementedError

    def from_dict(self, dct):
        raise NotImplementedError


class BpmnDataSpecificationConverter(BpmnSpecConverter):
    """This is the base Data Spec converter.

    Currently the only use is Data Objects.
    """

    def to_dict(self, data_spec):
        return { 'bpmn_id': data_spec.bpmn_id, 'bpmn_name': data_spec.bpmn_name }

    def from_dict(self, dct):
        return self.spec_class(**dct)


class EventDefinitionConverter(BpmnSpecConverter):
    """This is the base Event Defintiion Converter.

    It provides conversions for the great majority of BPMN events as-is, and contains
    one custom method for serializing Correlation Properties (as Message Event Defintiions
    are likely to the most commonly extended event definition spec).
    """

    def to_dict(self, event_definition):
        dct = {
            'description': event_definition.description,
            'name': event_definition.name
        }
        return dct

    def from_dict(self, dct):
        event_definition = self.spec_class(**dct)
        return event_definition

    def correlation_properties_to_dict(self, props):
        return [prop.__dict__ for prop in props]

    def correlation_properties_from_dict(self, props):
        return [CorrelationProperty(**prop) for prop in props]


class TaskSpecConverter(BpmnSpecConverter):
    """
    This the base Task Spec Converter.

    It contains methods for parsing generic and BPMN task spec attributes.

    If you have extended any of the the BPMN tasks with custom functionality, you'll need to
    implement a converter for those task spec types.  You'll need to implement the `to_dict` and
    `from_dict` methods on any inheriting classes.

    The default task spec converters are in the `task`, 'process_spec`, and 'event_definitions`
    modules of this package; the `camunda`,`dmn`, and `spiff` serialization packages contain other 
    examples.
    """
    def get_default_attributes(self, spec):
        """Extracts the default Spiff attributes from a task spec.

        :param spec: the task spec to be converted

        Returns:
            a dictionary of standard task spec attributes
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
            'data_input_associations': [ self.registry.convert(obj) for obj in spec.data_input_associations ],
            'data_output_associations': [ self.registry.convert(obj) for obj in spec.data_output_associations ],
            'io_specification': self.registry.convert(spec.io_specification),
        }

    def get_join_attributes(self, spec):
        """Extracts attributes for task specs that inherit from `Join`.

        :param spec: the task spec to be converted

        Returns:
            a dictionary of `Join` task spec attributes
        """
        return {
            'split_task': spec.split_task,
            'threshold': spec.threshold,
            'cancel': spec.cancel_remaining,
        }

    def get_subworkflow_attributes(self, spec):
        """Extracts attributes for task specs that inherit from `SubWorkflowTask`.

        :param spec: the task spec to be converted

        Returns:
            a dictionary of subworkflow task spec attributes
        """
        return {'spec': spec.spec}

    def get_standard_loop_attributes(self, spec):
        """Extracts attributes for standard loop tasks.
        
        :param spec: the task spec to be converted

        Returns:
            a dictionary of standard loop task spec attributes
        """
        return {
            'task_spec': spec.task_spec,
            'maximum': spec.maximum,
            'condition': spec.condition,
            'test_before': spec.test_before,
        }
    
    def task_spec_from_dict(self, dct):
        """
        Creates a task spec based on the supplied dictionary.  It handles setting the default
        task spec attributes as well as attributes added by `BpmnSpecMixin`.

        :param dct: the dictionary to create the task spec from

        Returns:
            a restored task spec
        """
        dct['data_input_associations'] = self.registry.restore(dct.pop('data_input_associations', []))
        dct['data_output_associations'] = self.registry.restore(dct.pop('data_output_associations', []))

        inputs = dct.pop('inputs')
        outputs = dct.pop('outputs')

        wf_spec = dct.pop('wf_spec')
        name = dct.pop('name')
        bpmn_id = dct.pop('bpmn_id')

        spec = self.spec_class(wf_spec, name, **dct)
        spec._inputs = inputs
        spec._outputs = outputs

        if issubclass(self.spec_class, BpmnSpecMixin) and bpmn_id != name:
            # This is a hack for multiinstance tasks :(  At least it is simple.
            # Ideally I'd fix it in the parser, but I'm afraid of quickly running into a wall there
            spec.bpmn_id = bpmn_id

        if isinstance(spec, BpmnSpecMixin):
            spec.io_specification = self.registry.restore(dct.pop('io_specification', None))

        return spec


class WorkflowSpecConverter(BpmnSpecConverter):
    """
    This is the base converter for a BPMN workflow spec.

    It will register converters for the task spec types contained in the workflow, as well as
    the workflow spec class itself.

    This class can be extended if you implement a custom workflow spec type.  See the converter
    in `workflow_spec_converter` for an example.
    """

    def __init__(self, spec_class, registry):
        """
        Converter for a BPMN workflow spec class.

        The `to_dict` and `from_dict` methods of the given task spec converter classes will
        be registered, so that they can be restored automatically.

        The data_converter applied to task *spec* data, not task data, and may be `None`.  See
        `BpmnTaskSpecConverter` for more discussion.

        :param spec_class: the workflow spec class
        :param task_spec_converters: a list of `BpmnTaskSpecConverter` classes
        """
        super().__init__(spec_class, registry)

        # Leaving these as-as, as I can't imagine anyone would need or want to extend
        self.registry.register(Attrib, self.attrib_to_dict, partial(self.attrib_from_dict, Attrib))
        self.registry.register(PathAttrib, self.attrib_to_dict, partial(self.attrib_from_dict, PathAttrib))

    def attrib_to_dict(self, attrib):
        return { 'name': attrib.name }

    def attrib_from_dict(self, attrib_class, dct):
        return attrib_class(dct['name'])