from functools import partial

from SpiffWorkflow.bpmn.specs.BpmnProcessSpec import BpmnDataSpecification

from .dictionary import DictionaryConverter

from ...specs.events.event_definitions import (
    NoneEventDefinition,
    MultipleEventDefinition, 
    SignalEventDefinition, 
    MessageEventDefinition,
    CorrelationProperty,
    TimeDateEventDefinition,
    DurationTimerEventDefinition,
    CycleTimerEventDefinition,
    ErrorEventDefinition,
    EscalationEventDefinition,
    CancelEventDefinition,
    TerminateEventDefinition,
    NamedEventDefinition
)

from ...specs.BpmnSpecMixin import BpmnSpecMixin
from ....operators import Attrib, PathAttrib

class BpmnDataSpecificationConverter:

    @staticmethod
    def to_dict(data_spec):
        return { 'name': data_spec.name, 'description': data_spec.description }

    @staticmethod
    def from_dict(dct):
        return BpmnDataSpecification(**dct)



class TaskSpecConverter(DictionaryConverter):
    """
    This the base Task Spec Converter.

    It contains methods for parsing generic and BPMN task spec attributes.

    If you have extended any of the the BPMN tasks with custom functionality, you'll need to
    implement a converter for those task spec types.  You'll need to implement the `to_dict` and
    `from_dict` methods on any inheriting classes.

    The default task spec converters are in `task_converters`; the `camunda` and `dmn`
    serialization packages contain other examples.
    """

    def __init__(self, spec_class, data_converter, typename=None):
        """The default task spec converter.  This will generally be registered with a workflow
        spec converter.

        Task specs can contain arbitrary data, though none of the default BPMN tasks do.  We
        may remove this functionality in the future.  Therefore, the data_converter can be
        `None`; if this is the case, task spec attributes that can contain arbitrary data will be
        ignored.

        :param spec_class: the class defining the task type
        :param data_converter: a converter for custom data (can be None)
        :param typename: an optional typename for the object registration
        """
        super().__init__()
        self.spec_class = spec_class
        self.data_converter = data_converter
        self.typename = typename if typename is not None else spec_class.__name__

        event_definitions = [
            NoneEventDefinition,
            CancelEventDefinition,
            TerminateEventDefinition,
            SignalEventDefinition,
            MessageEventDefinition,
            ErrorEventDefinition,
            EscalationEventDefinition,
            TimeDateEventDefinition, 
            DurationTimerEventDefinition, 
            CycleTimerEventDefinition,
            MultipleEventDefinition
        ]

        for event_definition in event_definitions:
            self.register(
                event_definition,
                self.event_definition_to_dict,
                partial(self.event_defintion_from_dict, event_definition)
            )

        self.register(Attrib, self.attrib_to_dict, partial(self.attrib_from_dict, Attrib))
        self.register(PathAttrib, self.attrib_to_dict, partial(self.attrib_from_dict, PathAttrib))
        self.register(BpmnDataSpecification, BpmnDataSpecificationConverter.to_dict, BpmnDataSpecificationConverter.from_dict)

    def to_dict(self, spec):
        """
        The convert method that will be called when a Task Spec Converter is registered with a
        Workflow Spec Converter.
        """
        raise NotImplementedError

    def from_dict(self, dct):
        """
        The restore method that will be called when a Task Spec Converter is registered with a
        Workflow Spec Converter.
        """
        raise NotImplementedError

    def get_default_attributes(self, spec):
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
        if self.data_converter is not None:
            dct['data'] = self.data_converter.convert(spec.data)
            dct['defines'] = self.data_converter.convert(spec.defines)
            dct['pre_assign'] = self.data_converter.convert(spec.pre_assign)
            dct['post_assign'] = self.data_converter.convert(spec.post_assign)

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
            'data_input_associations': [ self.convert(obj) for obj in spec.data_input_associations ],
            'data_output_associations': [ self.convert(obj) for obj in spec.data_output_associations ],
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

    def task_spec_from_dict(self, dct):
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

        if self.data_converter is not None:
            spec.data = self.data_converter.restore(dct.get('data', {}))
            spec.defines = self.data_converter.restore(dct.get('defines', {}))
            spec.pre_assign = self.data_converter.restore(dct.get('pre_assign', {}))
            spec.post_assign = self.data_converter.restore(dct.get('post_assign', {}))

        if isinstance(spec, BpmnSpecMixin):
            spec.documentation = dct.pop('documentation', None)
            spec.lane = dct.pop('lane', None)
            spec.loopTask = dct.pop('loopTask', False)
            spec.data_input_associations = self.restore(dct.pop('data_input_associations', []))
            spec.data_output_associations = self.restore(dct.pop('data_output_associations', []))

        return spec

    def event_definition_to_dict(self, event_definition):
        """
        Converts an BPMN event definition to a dict.  It will not typically be called directly,
        but via `convert` and will convert any event type supported by Spiff.

        :param event_definition: the event_definition to be converted.

        Returns:
            a dictionary representation of an event definition
        """
        dct = {'internal': event_definition.internal, 'external': event_definition.external}

        if isinstance(event_definition, NamedEventDefinition):
            dct['name'] = event_definition.name
        if isinstance(event_definition, MessageEventDefinition):
            dct['correlation_properties'] = [prop.__dict__ for prop in event_definition.correlation_properties]
        if isinstance(event_definition, (TimeDateEventDefinition, DurationTimerEventDefinition, CycleTimerEventDefinition)):
            dct['name'] = event_definition.name
            dct['expression'] = event_definition.expression
        if isinstance(event_definition, ErrorEventDefinition):
            dct['error_code'] = event_definition.error_code
        if isinstance(event_definition, EscalationEventDefinition):
            dct['escalation_code'] = event_definition.escalation_code
        if isinstance(event_definition, MultipleEventDefinition):
            dct['event_definitions'] = [self.convert(e) for e in event_definition.event_definitions]
            dct['parallel'] = event_definition.parallel

        return dct

    def event_defintion_from_dict(self, definition_class, dct):
        """Restores an event definition.  It will not typically be called directly, but via
        `restore` and will restore any BPMN event type supporred by Spiff.

        :param definition_class: the class that will be used to create the object
        :param dct: the event definition attributes

        Returns:
            an `EventDefinition` object
        """
        internal, external = dct.pop('internal'), dct.pop('external')
        if 'correlation_properties' in dct:
            dct['correlation_properties'] = [CorrelationProperty(**prop) for prop in dct['correlation_properties']]
        if 'event_definitions' in dct:
            dct['event_definitions'] = [self.restore(d) for d in dct['event_definitions']]
        event_definition = definition_class(**dct)
        event_definition.internal = internal
        event_definition.external = external
        return event_definition

    def attrib_to_dict(self, attrib):
        return { 'name': attrib.name }

    def attrib_from_dict(self, attrib_class, dct):
        return attrib_class(dct['name'])
