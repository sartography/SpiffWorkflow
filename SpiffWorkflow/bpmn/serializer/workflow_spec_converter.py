from .bpmn_converters import BpmnWorkflowSpecConverter

from ..specs.BpmnProcessSpec import BpmnProcessSpec
from ..specs.MultiInstanceTask import MultiInstanceTask, getDynamicMIClass
from ..specs.BpmnSpecMixin import BpmnSpecMixin
from ..specs.events.IntermediateEvent import _BoundaryEventParent

from ...operators import Attrib, PathAttrib
from ...specs.WorkflowSpec import WorkflowSpec


class BpmnProcessSpecConverter(BpmnWorkflowSpecConverter):

    def __init__(self, task_spec_converters, data_converter=None):
        super().__init__(BpmnProcessSpec, task_spec_converters, data_converter)
        self.register(WorkflowSpec, self.base_workflow_spec_to_dict, self.from_dict)

    def multi_instance_to_dict(self, spec):

        # This is a hot mess, but I don't know how else to deal with the dynamically
        # generated classes.  Why do we use them?
        classname = spec.prevtaskclass.split('.')[-1]
        # Bypass the automatic selection of a conversion function
        # This returns the partial function that was created on register for the original task type.
        # The second argument is the function that would be called by `convert`.
        conversion = self.convert_to_dict[classname]
        func = conversion.args[1]
        # We can just call it directly and add the typename manually
        dct = func(spec)
        dct['typename'] = classname
        # And we have to do this here, rather than in a converter
        # We also have to manually apply the Attrib conversions
        convert_attrib = lambda v: { 'name': v.name, 'typename': v.__class__.__name__ }
        dct.update({
            'times': convert_attrib(spec.times) if spec.times is not None else None,
            'elementVar': spec.elementVar,
            'collection': convert_attrib(spec.collection) if spec.collection is not None else None,
            # These are not defined in the constructor, but added by the parser, or somewhere else inappropriate
            'completioncondition': spec.completioncondition,
            'prevtaskclass': spec.prevtaskclass,
            'isSequential': spec.isSequential,
        })
        # Also from the parser, but not always present.
        if hasattr(spec, 'expanded'):
            dct['expanded'] = spec.expanded
        return dct

    def multiinstance_from_dict(self, dct):

        # The restore function removes items from the dictionary.
        # We need the original so that we can restore everything without enumerating all
        # possibiliies in this function.
        attrs = list(dct.keys())
        attrs.remove('typename')
        attrs.remove('wf_spec')
        # These need to be restored here
        attrs.remove('times')
        attrs.remove('collection')
        # If only I'd done this right in the DMN converter I wouldn't have to pollute this on with
        # task specific cases.
        if 'decision_table' in attrs:
            attrs.remove('decision_table')
            attrs.append('dmnEngine')

        # Terrible ugly hack
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
        # Restore the attributes that weren't recognized by the original converter
        restore_attrib = lambda v: Attrib(v['name']) if v['typename'] == 'Attrib' else PathAttrib(v['name'])
        task_spec.times = restore_attrib(dct['times']) if dct['times'] is not None else None
        task_spec.collection = restore_attrib(dct['collection']) if dct['collection'] is not None else None
        # Now copy everything else, from the temporary task spec if possible, otherwise the dict
        for attr in attrs:
            # If the original task has the attr, use the converted value
            if hasattr(original, attr):
                task_spec.__dict__[attr] = original.__dict__[attr]
            else:
                task_spec.__dict__[attr] = self.restore(dct[attr])

        # Handle adding any remaining attributes from the original task type that might not be
        # present in the restored version (for example attributes added since last serialized)
        for attr in original.__dict__:
            if not hasattr(task_spec, attr):
                task_spec.__dict__[attr] = original.__dict__[attr]

        return task_spec

    def convert_task_spec_extensions(self, task_spec, dct):
        # Extensions will be moved out of the base parser, but since we currently add them to some
        # indeterminate set of tasks, we'll just check all the tasks for them here.
        if hasattr(task_spec, 'extensions'):
            dct.update({'extensions': task_spec.extensions})

    def restore_task_spec_extensions(self, dct, task_spec):
        if 'extensions' in dct:
            task_spec.extensions = dct.pop('extensions')

    def to_dict(self, spec):

        dct = {
            'name': spec.name,
            'description': spec.description,
            'file': spec.file,
            'task_specs': {},
            'data_inputs': [ self.convert(obj) for obj in spec.data_inputs ],
            'data_outputs': [ self.convert(obj) for obj in spec.data_outputs ],
            'data_objects': dict([ (name, self.convert(obj)) for name, obj in spec.data_objects .items() ]),
            'correlation_keys': spec.correlation_keys,
        }
        for name, task_spec in spec.task_specs.items():
            if isinstance(task_spec, MultiInstanceTask):
                task_dict = self.multi_instance_to_dict(task_spec)
            else:
                task_dict = self.convert(task_spec)
            self.convert_task_spec_extensions(task_spec, task_dict)
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

        # Add the data specs
        spec.data_inputs = [ self.restore(obj_dct) for obj_dct in dct.pop('data_inputs', []) ]
        spec.data_outputs = [ self.restore(obj_dct) for obj_dct in dct.pop('data_outputs', []) ]
        # fixme:  This conditional can be removed in the next release, just avoiding invalid a potential
        #  serialization issue for some users caught between official releases.
        if isinstance(dct.get('data_objects', {}), dict):
            spec.data_objects = dict([ (name, self.restore(obj_dct)) for name, obj_dct in dct.pop('data_objects', {}).items() ])
        else:
            spec.data_objects = {}

        # Add messaging related stuff
        spec.correlation_keys = dct.pop('correlation_keys', {})

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
            if name == 'Start':
                spec.start = task_spec
            self.restore_task_spec_extensions(task_dict, task_spec)

        # Now we have to go back and fix all the circular references to everything
        for task_spec in spec.task_specs.values():
            if isinstance(task_spec, BpmnSpecMixin):
                for flow in task_spec.outgoing_sequence_flows.values():
                    flow.target_task_spec = spec.get_task_spec_from_name(flow.target_task_spec)
                for flow in task_spec.outgoing_sequence_flows_by_id.values():
                    flow.target_task_spec = spec.get_task_spec_from_name(flow.target_task_spec)
            if isinstance(task_spec, _BoundaryEventParent):
                task_spec.main_child_task_spec = spec.get_task_spec_from_name(task_spec.main_child_task_spec)
            task_spec.inputs = [ spec.get_task_spec_from_name(name) for name in task_spec.inputs ]
            task_spec.outputs = [ spec.get_task_spec_from_name(name) for name in task_spec.outputs ]

        return spec

    def base_workflow_spec_to_dict(self, spec):

        # We should delete this method when we stop supporting the old serializer.
        # It uses WorkflowSpec rather than BpmnWorkflowSpec, which does not support data objects.
        # I hate copying this code here, but I am NOT putting an "if isinstance" check in the
        # main method to handle a bug in the thing I'm replacing,

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
            self.convert_task_spec_extensions(task_spec, task_dict)
            dct['task_specs'][name] = task_dict

        return dct
