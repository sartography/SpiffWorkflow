from functools import partial

from uuid import UUID
from datetime import datetime, timedelta

from .dictionary import DictionaryConverter

from ..specs.events import SignalEventDefinition, MessageEventDefinition, NoneEventDefinition
from ..specs.events import TimerEventDefinition, CycleTimerEventDefinition, TerminateEventDefinition
from ..specs.events import ErrorEventDefinition, EscalationEventDefinition, CancelEventDefinition
from ..specs.events.event_definitions import NamedEventDefinition

from ..specs.SubWorkflowTask import SubWorkflowTask
from ..specs.MultiInstanceTask import MultiInstanceTask, getDynamicMIClass
from ..specs.BpmnSpecMixin import BpmnSpecMixin, SequenceFlow
from ..specs.events.IntermediateEvent import _BoundaryEventParent

from ...operators import Attrib, PathAttrib

class BpmnDataConverter(DictionaryConverter):

    def __init__(self):

        super().__init__()
        self.register(UUID, lambda v: { 'value': str(v) }, lambda v: UUID(v['value']))
        self.register(datetime, lambda v:  { 'value': v.isoformat() }, lambda v: datetime.fromisoformat(v['value']))
        self.register(timedelta, lambda v: { 'days': v.days, 'seconds': v.seconds }, lambda v: timedelta(**v))


class BpmnTaskSpecConverter(DictionaryConverter):

    def __init__(self, spec_class, data_converter, typename=None):

        super().__init__()
        self.spec_class = spec_class
        self.data_converter = data_converter
        self.typename = typename if typename is not None else spec_class.__name__
        
        event_definitions = [ NoneEventDefinition, CancelEventDefinition, TerminateEventDefinition,
            SignalEventDefinition, MessageEventDefinition, ErrorEventDefinition, EscalationEventDefinition,
            TimerEventDefinition, CycleTimerEventDefinition ]

        for event_definition in event_definitions:
            self.register(
                event_definition,
                self.event_definition_to_dict, 
                partial(self.event_defintion_from_dict, event_definition)
            )
    
    def to_dict(self, spec):
        raise NotImplementedError

    def from_dict(self, dct):
        raise NotImplementedError

    def get_default_attributes(self, spec):
        
        # Defined in base task spec; all tasks should have these attributes
        dct = {
            'id': spec.id,
            'name': spec.name,
            'description': spec.description,
            'manual': spec.manual,
            'internal': spec.internal,
            'position': spec.internal,
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

        # Bpmn tasks add these atrributes
        return {
            'lane': spec.lane,
            'documentation': spec.documentation,
            'loopTask': spec.loopTask,
            'outgoing_sequence_flows': dict(
                (k, self.sequence_flow_to_dict(v)) for k, v in spec.outgoing_sequence_flows.items()
            ),
            'outgoing_sequence_flows_by_id': dict(
                (k, self.sequence_flow_to_dict(v)) for k, v in spec.outgoing_sequence_flows_by_id.items()
            )
        }

    def get_join_attributes(self, spec):

        return {
            'split_task': spec.split_task,
            'threshold': spec.threshold,
            'cancel': spec.cancel_remaining,
        }

    def get_subworkflow_attributes(self, spec):

        return {
            'spec': spec.spec,
            'sub_workflow': spec.sub_workflow,
        }

    def event_definition_to_dict(self, event_definition):

        dct = {'internal': event_definition.internal, 'external': event_definition.external}

        if isinstance(event_definition, NamedEventDefinition):
            dct['name'] = event_definition.name
        if isinstance(event_definition, MessageEventDefinition):
            dct['payload'] = event_definition.payload
            dct['result_var'] = event_definition.result_var
        if isinstance(event_definition, TimerEventDefinition):
            dct['label'] = event_definition.label
            dct['dateTime'] = event_definition.dateTime
        if isinstance(event_definition, CycleTimerEventDefinition):
            dct['label'] = event_definition.label
            dct['cycle_definition'] = event_definition.cycle_definition
        if isinstance(event_definition, ErrorEventDefinition):
            dct['error_code'] = event_definition.error_code
        if isinstance(event_definition, EscalationEventDefinition):
            dct['escalation_code'] = event_definition.escalation_code

        return dct

    def sequence_flow_to_dict(self, flow):
        
        return {
            'id': flow.id,
            'name': flow.name,
            'documentation': flow.documentation,
            'target_task_spec': flow.target_task_spec.name
        }

    def task_spec_from_dict(self, dct):

        internal = dct.pop('internal')
        inputs = dct.pop('inputs')
        outputs = dct.pop('outputs')

        spec = self.spec_class(**dct)
        spec.internal = internal
        spec.inputs = inputs
        spec.outputs = outputs

        if self.data_converter is not None:
            spec.data = self.data_converter.restore(dct.get('data', {}))
            spec.defines = self.data_converter.restore(dct.get('defines', {}))
            spec.pre_assign = self.data_converter.restore(dct.get('pre_assign', {}))
            spec.post_assign = self.data_converter.restore(dct.get('post_assign', {}))

        if isinstance(spec, BpmnSpecMixin):
            spec.documentation = dct.pop('documentation', None)
            spec.lane = dct.pop('lane', None)
            spec.loopTask = dct.pop('loopTask', False)

        return spec

    def event_defintion_from_dict(self, definition_class, dct):

        internal, external = dct.pop('internal'), dct.pop('external')
        event_definition = definition_class(**dct)
        event_definition.internal = internal
        event_definition.external = external
        return event_definition


class BpmnWorkflowSpecConverter(DictionaryConverter):

    def __init__(self, spec_class, task_spec_converters, data_converter=None):

        super().__init__()
        self.spec_class = spec_class
        self.data_converter = data_converter

        self.register(spec_class, self.to_dict, self.from_dict)
        for converter in task_spec_converters:
            self.register(converter.spec_class, converter.to_dict, converter.from_dict, converter.typename)

        # For multiinstance tasks
        self.register(Attrib, self.attrib_to_dict, partial(self.attrib_from_dict, Attrib))
        self.register(PathAttrib, self.attrib_to_dict, partial(self.attrib_from_dict, PathAttrib))

    def multi_instance_to_dict(self, spec):

        # This is a hot mess, but I don't know how else to deal with the dynamically 
        # generated classes.  Why do we use them?
        classname = spec.prevtaskclass
        registered = dict((f'{c.__module__}.{c.__name__}', c) for c in self.typenames)
        self.typenames[spec.__class__] = self.typenames[registered[classname]]
        dct = self.convert(spec)
        # And we have to do this here, rather than in a converter, because
        dct.update({
            'times': self.convert(spec.times),
            'elementVar': spec.elementVar,
            'collection': self.convert(spec.collection),
            # These are not defined in the constructor, but added by the parser, or somewhere else inappropriate
            'completioncondition': spec.completioncondition,
            'prevtaskclass': spec.prevtaskclass,
            'isSequential': spec.isSequential,
        })
        # Also from the parser, but not always present.
        if hasattr(spec, 'exapnded'):
            dct['expanded'] = spec.expanded
        return dct

    def multiinstance_from_dict(self, dct):

        registered = dict((name, c) for c, name in self.typenames.items())
        # First get the dynamic class
        cls = getDynamicMIClass(dct['name'], registered[dct['typename']])
        # Restore the task according to the original task spec, so that its attributes can be converted
        # recursively
        original = self.restore(dct.copy())
        # But this task has the wrong class, so delete it from the spec
        del dct['wf_spec'].task_specs[original.name]
        # Create a new class using the dynamic class
        task_spec = cls(**dct)
        # Set attributes that were added during initialization
        task_spec.times = self.restore(task_spec.times)
        task_spec.collection = self.restore(task_spec.collection)
        task_spec.elementVar = dct['elementVar']
        # Now copy values from the task dictionary that do not appear in the new task
        for attr, val in dct.items():
            if not hasattr(task_spec, attr):
                # If the original task has the attr, use the converted value
                if hasattr(original, attr):
                    task_spec.__dict__[attr] = original.__dict__[attr]
                else:
                    task_spec.__dict__[attr] = self.restore(val)

        return task_spec

    def to_dict(self, spec):

        dct = {
            'name': spec.name,
            'description': spec.description,
            'file': spec.file,
            'task_specs': {},
        }
        for name, task_spec in spec.task_specs.items():
            if isinstance(task_spec, MultiInstanceTask):
                task_dict = self.multi_instance_to_dict(task_spec)
            else:
                task_dict = self.convert(task_spec)
            if isinstance(task_spec, SubWorkflowTask):
                task_dict['spec'] = self.convert(task_spec.spec)
                task_dict['sub_workflow'] = task_spec.sub_workflow.name if task_spec.sub_workflow is not None else None
            dct['task_specs'][name] = task_dict

        return dct

    def from_dict(self, dct):

        spec = self.spec_class(name=dct['name'], description=dct['description'], filename=dct['file'])
        # There a nostart arg in the base workflow spec class that prevents start task creation, but
        # the BPMN process spec doesn't pass it in, so we have to delete the auto generated Start task.
        del spec.task_specs['Start']
        spec.start = None
        
        # These are also automatically created with a workflow and should be replaced
        del spec.task_specs['End']
        del spec.task_specs[f'{spec.name}.EndJoin']

        for name, task_dict in dct['task_specs'].items():
            # I hate this, but I need to pass in the workflow spec when I create the task.
            # IMO storing the workflow spec on the task spec is a TERRIBLE idea, but that's
            # how this thing works.
            task_dict['wf_spec'] = spec
            # Ugh.
            if 'prevtaskclass' in task_dict:
                task_spec = self.multiinstance_from_dict(task_dict)
            else:
                task_spec = self.restore(task_dict)
            spec.task_specs[name] = task_spec
            if name == 'Start':
                spec.start = task_spec
            if isinstance(task_spec, SubWorkflowTask):
                task_spec.spec = self.restore(task_spec.spec)

        # Now we have to go back and fix all the circular references to everything
        for task_spec in spec.task_specs.values():
            if isinstance(task_spec, BpmnSpecMixin):
                for name, flow_dict in task_spec.outgoing_sequence_flows.items():
                    flow_dict['target_task_spec'] = spec.get_task_spec_from_name(name)
                    task_spec.outgoing_sequence_flows[name] = SequenceFlow(**flow_dict)
                for flow_id, flow_dict in task_spec.outgoing_sequence_flows_by_id.items():
                    flow_dict['target_task_spec'] = spec.get_task_spec_from_name(name)
                    task_spec.outgoing_sequence_flows_by_id[flow_id] = SequenceFlow(**flow_dict)         
            if isinstance(task_spec, _BoundaryEventParent):
                task_spec.main_child_task_spec = spec.get_task_spec_from_name(task_spec.main_child_task_spec)
            task_spec.inputs = [ spec.get_task_spec_from_name(name) for name in task_spec.inputs ]
            task_spec.outputs = [ spec.get_task_spec_from_name(name) for name in task_spec.outputs ]
        
        return spec

    def attrib_to_dict(self, attrib):
        return { 'name': attrib.name }

    def attrib_from_dict(self, attrib_class, dct):
        return attrib_class(dct['name'])