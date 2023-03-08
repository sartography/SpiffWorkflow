from ..specs.BpmnProcessSpec import BpmnProcessSpec
from ..specs.events.IntermediateEvent import _BoundaryEventParent

from .helpers.spec import WorkflowSpecConverter

class BpmnProcessSpecConverter(WorkflowSpecConverter):

    def __init__(self, registry):
        super().__init__(BpmnProcessSpec, registry)

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
            'io_specification': self.registry.convert(spec.io_specification),
            'data_objects': dict([ (name, self.registry.convert(obj)) for name, obj in spec.data_objects.items() ]),
            'correlation_keys': spec.correlation_keys,
        }
        for name, task_spec in spec.task_specs.items():
            task_dict = self.registry.convert(task_spec)
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
        spec.io_specification = self.registry.restore(dct.pop('io_specification', None))
        # fixme:  This conditional can be removed in the next release, just avoiding invalid a potential
        #  serialization issue for some users caught between official releases.
        if isinstance(dct.get('data_objects', {}), dict):
            spec.data_objects = dict([ (name, self.registry.restore(obj_dct)) for name, obj_dct in dct.pop('data_objects', {}).items() ])
        else:
            spec.data_objects = {}

        # Add messaging related stuff
        spec.correlation_keys = dct.pop('correlation_keys', {})

        for name, task_dict in dct['task_specs'].items():
            # I hate this, but I need to pass in the workflow spec when I create the task.
            # IMO storing the workflow spec on the task spec is a TERRIBLE idea, but that's
            # how this thing works.
            task_dict['wf_spec'] = spec
            task_spec = self.registry.restore(task_dict)
            if name == 'Start':
                spec.start = task_spec
            self.restore_task_spec_extensions(task_dict, task_spec)

        # Now we have to go back and fix all the circular references to everything
        for task_spec in spec.task_specs.values():
            if isinstance(task_spec, _BoundaryEventParent):
                task_spec.main_child_task_spec = spec.get_task_spec_from_name(task_spec.main_child_task_spec)
            task_spec.inputs = [ spec.get_task_spec_from_name(name) for name in task_spec.inputs ]
            task_spec.outputs = [ spec.get_task_spec_from_name(name) for name in task_spec.outputs ]

        return spec
