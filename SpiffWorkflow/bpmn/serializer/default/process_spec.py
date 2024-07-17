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

from ..helpers.bpmn_converter import BpmnConverter
from SpiffWorkflow.bpmn.specs.mixins.multiinstance_task import LoopTask


class BpmnProcessSpecConverter(BpmnConverter):

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
            dct['task_specs'][name] = task_dict

        return dct

    def from_dict(self, dct):

        spec = self.target_class(name=dct['name'], description=dct['description'], filename=dct['file'])
        # These are automatically created with a workflow and should be replaced
        del spec.task_specs['Start']
        spec.start = None
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

        loop_tasks = []
        dct['task_specs'].pop('Root', None)
        for name, task_dict in dct['task_specs'].items():
            # I hate this, but I need to pass in the workflow spec when I create the task.
            # IMO storing the workflow spec on the task spec is a TERRIBLE idea, but that's
            # how this thing works.
            task_dict['wf_spec'] = spec
            task_spec = self.registry.restore(task_dict)
            if name == 'Start':
                spec.start = task_spec
            if isinstance(task_spec, LoopTask):
                loop_tasks.append(task_spec)
            self.restore_task_spec_extensions(task_dict, task_spec)

        for task_spec in loop_tasks:
            child_spec = spec.task_specs.get(task_spec.task_spec)
            child_spec.completed_event.connect(task_spec.merge_child)

        return spec
