from functools import partial

from ...specs.BpmnSpecMixin import BpmnSpecMixin
from ...specs.events.event_definitions import NamedEventDefinition, TimerEventDefinition
from ...specs.events.event_definitions import CorrelationProperty
from ....operators import Attrib, PathAttrib


class BpmnSpecConverter:

    def __init__(self, spec_class, registry, typename=None):

        self.spec_class = spec_class
        self.registry = registry
        self.typename = typename if typename is not None else spec_class.__name__     
        self.registry.register(spec_class, self.to_dict, self.from_dict, self.typename)   

    def to_dict(self, spec):
        raise NotImplementedError

    def from_dict(self, dct):
        raise NotImplementedError


class BpmnDataSpecificationConverter(BpmnSpecConverter):

    def to_dict(self, data_spec):
        return { 'name': data_spec.name, 'description': data_spec.description }

    def from_dict(self, dct):
        return self.spec_class(**dct)


class EventDefinitionConverter(BpmnSpecConverter):

    def to_dict(self, event_definition):
        dct = {'internal': event_definition.internal, 'external': event_definition.external}
        if isinstance(event_definition, (NamedEventDefinition, TimerEventDefinition)):
            dct['name'] = event_definition.name
        return dct

    def from_dict(self, dct):
        internal, external = dct.pop('internal'), dct.pop('external')
        event_definition = self.spec_class(**dct)
        event_definition.internal = internal
        event_definition.external = external
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

    The default task spec converters are in `task_converters`; the `camunda` and `dmn`
    serialization packages contain other examples.
    """
    def get_default_attributes(self, spec, include_data=False):
        """Extracts the default Spiff attributes from a task spec.

        :param spec: the task spec to be converted

        Returns:
            a dictionary of standard task spec attributes
        """
        dct = {
            'id': spec.id,
            'name': spec.name,
            'description': spec.description,
            'manual': spec.manual,
            'internal': spec.internal,
            'lookahead': spec.lookahead,
            'inputs': [task.name for task in spec.inputs],
            'outputs': [task.name for task in spec.outputs],
        }
        # This stuff is also all defined in the base task spec, but can contain data, so we need
        # our data serializer.  I think we should try to get this stuff out of the base task spec.
        if include_data:
            dct['data'] = self.registry.convert(spec.data)
            dct['defines'] = self.registry.convert(spec.defines)
            dct['pre_assign'] = self.registry.convert(spec.pre_assign)
            dct['post_assign'] = self.registry.convert(spec.post_assign)

        return dct

    def get_bpmn_attributes(self, spec):
        """Extracts the attributes added by the `BpmnSpecMixin` class.

        :param spec: the task spec to be converted

        Returns:
            a dictionary of BPMN task spec attributes
        """
        return {
            'lane': spec.lane,
            'documentation': spec.documentation,
            'loopTask': spec.loopTask,
            'position': spec.position,
            'data_input_associations': [ self.registry.convert(obj) for obj in spec.data_input_associations ],
            'data_output_associations': [ self.registry.convert(obj) for obj in spec.data_output_associations ],
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

    def task_spec_from_dict(self, dct, include_data=False):
        """
        Creates a task spec based on the supplied dictionary.  It handles setting the default
        task spec attributes as well as attributes added by `BpmnSpecMixin`.

        :param dct: the dictionary to create the task spec from

        Returns:
            a restored task spec
        """
        internal = dct.pop('internal')
        inputs = dct.pop('inputs')
        outputs = dct.pop('outputs')

        spec = self.spec_class(**dct)
        spec.internal = internal
        spec.inputs = inputs
        spec.outputs = outputs
        spec.id = dct['id']

        if include_data:
            spec.data = self.registry.restore(dct.get('data', {}))
            spec.defines = self.registry.restore(dct.get('defines', {}))
            spec.pre_assign = self.registry.restore(dct.get('pre_assign', {}))
            spec.post_assign = self.registry.restore(dct.get('post_assign', {}))

        if isinstance(spec, BpmnSpecMixin):
            spec.documentation = dct.pop('documentation', None)
            spec.lane = dct.pop('lane', None)
            spec.loopTask = dct.pop('loopTask', False)
            spec.data_input_associations = self.registry.restore(dct.pop('data_input_associations', []))
            spec.data_output_associations = self.registry.restore(dct.pop('data_output_associations', []))

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