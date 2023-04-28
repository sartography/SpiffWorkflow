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

import json
import gzip
from copy import deepcopy
from uuid import UUID

from ..workflow import BpmnMessage, BpmnWorkflow
from ..specs.SubWorkflowTask import SubWorkflowTask
from ...task import Task

from .migration.version_migration import MIGRATIONS
from .helpers.registry import DefaultRegistry
from .helpers.dictionary import DictionaryConverter

from .process_spec import BpmnProcessSpecConverter
from .data_spec import BpmnDataObjectConverter, TaskDataReferenceConverter, IOSpecificationConverter
from .task_spec import DEFAULT_TASK_SPEC_CONVERTER_CLASSES
from .event_definition import DEFAULT_EVENT_CONVERTERS

DEFAULT_SPEC_CONFIG = {
    'process': BpmnProcessSpecConverter,
    'data_specs': [IOSpecificationConverter, BpmnDataObjectConverter, TaskDataReferenceConverter],
    'task_specs': DEFAULT_TASK_SPEC_CONVERTER_CLASSES,
    'event_definitions': DEFAULT_EVENT_CONVERTERS,
}


class BpmnWorkflowSerializer:
    """
    This class implements a customizable BPMN Workflow serializer, based on a Workflow Spec Converter
    and a Data Converter.

    The goal is to provide modular serialization capabilities.

    You'll need to configure a Workflow Spec Converter with converters for any task, data, or event types
    present in your workflows.

    If you have implemented any custom specs, you'll need to write a converter to handle them and
    replace the converter from the default confiuration with your own.

    If your workflow contains non-JSON-serializable objects, you'll need to extend or replace the
    default data converter with one that will handle them.  This converter needs to implement
    `convert` and `restore` methods.

    Serialization occurs in two phases: the first is to convert everything in the workflow to a
    dictionary containing only JSON-serializable objects and the second is dumping to JSON.

    This means that you can call the `workflow_to_dict` or `workflow_from_dict` methods separately from
    conversion to JSON for further manipulation of the state, or selective serialization of only certain
    parts of the workflow more conveniently.  You can of course call methods from the Workflow Spec and
    Data Converters via the `spec_converter` and `data_converter` attributes as well to bypass the
    overhead of converting or restoring the entire thing.
    """

    # This is the default version set on the workflow, it can be overwritten
    # using the configure_workflow_spec_converter.
    VERSION = "1.2"
    VERSION_KEY = "serializer_version"
    DEFAULT_JSON_ENCODER_CLS = None
    DEFAULT_JSON_DECODER_CLS = None

    @staticmethod
    def configure_workflow_spec_converter(spec_config=None, registry=None):
        """
        This method can be used to create a spec converter that uses custom specs.

        The task specs may contain arbitrary data, though none of the default task specs use it.  We don't
        recommend that you do this, as we may disallow it in the future.  However, if you have task spec data,
        then you'll also need to make sure it can be serialized.

        The workflow spec serializer is based on the `DictionaryConverter` in the `helpers` package.  You can
        create one of your own, add custom data serializtion to that and pass that in as the `registry`.  The
        conversion classes in the spec_config will be added this "registry" and any classes with entries there
        will be serialized/deserialized.

        See the documentation for `helpers.spec.BpmnSpecConverter` for more information about what's going
        on here.

        :param spec_config: a dictionary specifying how to save and restore any classes used by the spec
        :param registry: a `DictionaryConverter` with conversions for custom data (if applicable)
        """
        config = spec_config or DEFAULT_SPEC_CONFIG
        spec_converter = registry or DictionaryConverter()
        config['process'](spec_converter)
        for cls in config['data_specs'] + config['task_specs'] + config['event_definitions']:
            cls(spec_converter)
        return spec_converter

    def __init__(self, spec_converter=None, data_converter=None, wf_class=None, version=VERSION,
                 json_encoder_cls=DEFAULT_JSON_ENCODER_CLS, json_decoder_cls=DEFAULT_JSON_DECODER_CLS):
        """Intializes a Workflow Serializer with the given Workflow, Task and Data Converters.

        :param spec_converter: the workflow spec converter
        :param data_converter: the data converter
        :param wf_class: the workflow class
        :param json_encoder_cls: JSON encoder class to be used for dumps/dump operations
        :param json_decoder_cls: JSON decoder class to be used for loads/load operations
        """
        super().__init__()
        self.spec_converter = spec_converter if spec_converter is not None else self.configure_workflow_spec_converter()
        self.data_converter = data_converter if data_converter is not None else DefaultRegistry()
        self.wf_class = wf_class if wf_class is not None else BpmnWorkflow
        self.json_encoder_cls = json_encoder_cls
        self.json_decoder_cls = json_decoder_cls
        self.VERSION = version

    def serialize_json(self, workflow, use_gzip=False):
        """Serialize the dictionary representation of the workflow to JSON.

        :param workflow: the workflow to serialize

        Returns:
            a JSON dump of the dictionary representation
        """
        dct = self.workflow_to_dict(workflow)
        dct[self.VERSION_KEY] = self.VERSION
        json_str = json.dumps(dct, cls=self.json_encoder_cls)
        return gzip.compress(json_str.encode('utf-8')) if use_gzip else json_str

    def __get_dict(self, serialization, use_gzip=False):
        if isinstance(serialization, dict):
            dct = serialization
        elif use_gzip:
            dct = json.loads(gzip.decompress(serialization), cls=self.json_decoder_cls)
        else:
            dct = json.loads(serialization, cls=self.json_decoder_cls)
        return dct

    def deserialize_json(self, serialization, use_gzip=False):
        dct = self.__get_dict(serialization, use_gzip)
        return self.workflow_from_dict(dct)

    def get_version(self, serialization, use_gzip=False):
        try:
            dct = self.__get_dict(serialization, use_gzip)
            if self.VERSION_KEY in dct:
                return dct[self.VERSION_KEY]
        except:  # Don't bail out trying to get a version, just return none.
            return None

    def workflow_to_dict(self, workflow):
        """Return a JSON-serializable dictionary representation of the workflow.

        :param workflow: the workflow

        Returns:
            a dictionary representation of the workflow
        """
        # These properties are applicable to top level & subprocesses
        dct = self.process_to_dict(workflow)
        # These are only used at the top-level
        dct['spec'] = self.spec_converter.convert(workflow.spec)
        dct['subprocess_specs'] = dict(
            (name, self.spec_converter.convert(spec)) for name, spec in workflow.subprocess_specs.items()
        )
        dct['subprocesses'] = dict(
            (str(task_id), self.process_to_dict(sp)) for task_id, sp in workflow.subprocesses.items()
        )
        dct['bpmn_messages'] = [self.message_to_dict(msg) for msg in workflow.bpmn_messages]

        dct['correlations'] = workflow.correlations
        return dct

    def workflow_from_dict(self, dct):
        """Create a workflow based on a dictionary representation.

        :param dct: the dictionary representation

        Returns:
            a BPMN Workflow object
        """
        dct_copy = deepcopy(dct)

        # Upgrade serialized version if necessary
        if self.VERSION_KEY in dct_copy:
            version = dct_copy.pop(self.VERSION_KEY)
            if version in MIGRATIONS:
                dct_copy = MIGRATIONS[version](dct_copy)

        # Restore the top level spec and the subprocess specs
        spec = self.spec_converter.restore(dct_copy.pop('spec'))
        subprocess_specs = dct_copy.pop('subprocess_specs', {})
        for name, wf_dct in subprocess_specs.items():
            subprocess_specs[name] = self.spec_converter.restore(wf_dct)

        # Create the top-level workflow
        workflow = self.wf_class(spec, subprocess_specs, deserializing=True)

        # Restore any unretrieve messages
        workflow.bpmn_messages = [ self.message_from_dict(msg) for msg in dct.get('bpmn_messages', []) ]

        workflow.correlations = dct_copy.pop('correlations', {})

        # Restore the remainder of the workflow
        workflow.data = self.data_converter.restore(dct_copy.pop('data'))
        workflow.success = dct_copy.pop('success')
        workflow.task_tree = self.task_tree_from_dict(dct_copy, dct_copy.pop('root'), None, workflow)

        return workflow

    def task_to_dict(self, task):
        return {
            'id': str(task.id),
            'parent': str(task.parent.id) if task.parent is not None else None,
            'children': [ str(child.id) for child in task.children ],
            'last_state_change': task.last_state_change,
            'state': task.state,
            'task_spec': task.task_spec.name,
            'triggered': task.triggered,
            'workflow_name': task.workflow.name,
            'internal_data': self.data_converter.convert(task.internal_data),
            'data': self.data_converter.convert(task.data),
        }

    def task_from_dict(self, dct, workflow, task_spec, parent):

        task = Task(workflow, task_spec, parent, dct['state'])
        task.id = UUID(dct['id'])
        task.last_state_change = dct['last_state_change']
        task.triggered = dct['triggered']
        task.internal_data = self.data_converter.restore(dct['internal_data'])
        task.data = self.data_converter.restore(dct['data'])
        return task

    def task_tree_to_dict(self, root):

        tasks = { }
        def add_task(task):
            dct = self.task_to_dict(task)
            tasks[dct['id']] = dct
            for child in task.children:
                add_task(child)

        add_task(root)
        return tasks

    def task_tree_from_dict(self, process_dct, task_id, parent_task, process, top_level_workflow=None, top_level_dct=None):

        top = top_level_workflow or process
        top_dct = top_level_dct or process_dct

        task_dict = process_dct['tasks'][task_id]
        task_spec = process.spec.task_specs[task_dict['task_spec']]
        task = self.task_from_dict(task_dict, process, task_spec, parent_task)
        if task_id == process_dct['last_task']:
            process.last_task = task

        if isinstance(task_spec, SubWorkflowTask) and task_id in top_dct.get('subprocesses', {}):
            subprocess_spec = top.subprocess_specs[task_spec.spec]
            subprocess = self.wf_class(subprocess_spec, {}, name=task_spec.name, parent=process, deserializing=True)
            subprocess_dct = top_dct['subprocesses'].get(task_id, {})
            subprocess.spec.data_objects.update(process.spec.data_objects)
            if len(subprocess.spec.data_objects) > 0:
                subprocess.data = process.data
            else:
                subprocess.data = self.data_converter.restore(subprocess_dct.pop('data'))
            subprocess.success = subprocess_dct.pop('success')
            subprocess.task_tree = self.task_tree_from_dict(subprocess_dct, subprocess_dct.pop('root'), None, subprocess, top, top_dct)
            subprocess.completed_event.connect(task_spec._on_subworkflow_completed, task)
            top_level_workflow.subprocesses[task.id] = subprocess

        for child_task_id in task_dict['children']:
            if child_task_id in process_dct['tasks']:
                child = process_dct['tasks'][child_task_id]
                self.task_tree_from_dict(process_dct, child_task_id, task, process, top, top_dct)
            else:
                raise ValueError(f"Task {task_id} ({task_spec.name}) has child {child_task_id}, but no such task exists")

        return task

    def process_to_dict(self, process):
        return {
            'data': self.data_converter.convert(process.data),
            'last_task': str(process.last_task.id) if process.last_task is not None else None,
            'success': process.success,
            'tasks': self.task_tree_to_dict(process.task_tree),
            'root': str(process.task_tree.id),
        }

    def message_to_dict(self, message):
        dct = {
            'correlations': dict([ (k, self.data_converter.convert(v)) for k, v in message.correlations.items() ]),
            'name': message.name,
            'payload': self.spec_converter.convert(message.payload),
        }
        return dct

    def message_from_dict(self, dct):
        return BpmnMessage(
            dict([ (k, self.data_converter.restore(v)) for k, v in dct['correlations'].items() ]),
            dct['name'],
            self.spec_converter.restore(dct['payload'])
        )
