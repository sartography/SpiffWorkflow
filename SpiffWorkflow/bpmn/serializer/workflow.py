import json
import gzip
from copy import deepcopy
from uuid import UUID

from .version_migration import MIGRATIONS

from .bpmn_converters import BpmnDataConverter

from ..workflow import BpmnMessage, BpmnWorkflow
from ..specs.SubWorkflowTask import SubWorkflowTask
from ...task import Task

from .workflow_spec_converter import BpmnProcessSpecConverter

from .task_spec_converters import SimpleTaskConverter, StartTaskConverter, EndJoinConverter, LoopResetTaskConverter
from .task_spec_converters import NoneTaskConverter, UserTaskConverter, ManualTaskConverter, ScriptTaskConverter
from .task_spec_converters import CallActivityTaskConverter, TransactionSubprocessTaskConverter
from .task_spec_converters import StartEventConverter, EndEventConverter
from .task_spec_converters import IntermediateCatchEventConverter, IntermediateThrowEventConverter
from .task_spec_converters import SendTaskConverter, ReceiveTaskConverter
from .task_spec_converters import BoundaryEventConverter, BoundaryEventParentConverter
from .task_spec_converters import ParallelGatewayConverter, ExclusiveGatewayConverter, InclusiveGatewayConverter

DEFAULT_TASK_SPEC_CONVERTER_CLASSES = [
    SimpleTaskConverter, StartTaskConverter, EndJoinConverter, LoopResetTaskConverter,
    NoneTaskConverter, UserTaskConverter, ManualTaskConverter, ScriptTaskConverter,
    CallActivityTaskConverter, TransactionSubprocessTaskConverter,
    StartEventConverter, EndEventConverter, SendTaskConverter, ReceiveTaskConverter,
    IntermediateCatchEventConverter, IntermediateThrowEventConverter,
    BoundaryEventConverter, BoundaryEventParentConverter,
    ParallelGatewayConverter, ExclusiveGatewayConverter, InclusiveGatewayConverter
]

class BpmnWorkflowSerializer:
    """
    This class implements a customizable BPMN Workflow serializer, based on a Workflow Spec Converter
    and a Data Converter.

    The goal is to provide modular serialization capabilities.

    You'll need to configure a Workflow Spec Converter with Task Spec Converters for any task types
    present in your workflows.  Because the Task Spec Converters also require initialization, the process
    of building a Workflow Spec Converter is a little tedious; therefore, this class provides a static
    method `configure_workflow_spec_converter` that can extend and/or override the default Task Spec
    Converter list and return a Workflow Spec Converter that will recognize the overridden specs.

    If you have implemented any custom task specs, you'll need to write a converter to handle them and
    provide it to this method; if you using only the defaults, you can call this with no arguments.

    If your workflow contains non-JSON-serializable objects, you'll need to extend or replace the
    default data converter with one that will handle them.  This converter needs to implement
    `convert` and `restore` methods.

    Serialization occurs in two phases: the first is to convert everything in the workflow to a
    dictionary containins only JSON-serializable objects and the second is dumping to JSON.

    This means that you can call the `workflow_to_dict` or `workflow_from_dict` methods separately from
    conversion to JSON for further manipulation of the state, or selective serialization of only certain
    parts of the workflow more conveniently.  You can of course call methods from the Workflow Spec and
    Data Converters via the `spec_converter` and `data_converter` attributes as well to bypass the
    overhead of converting or restoring the entire thing.
    """

    # This is the default version set on the workflow, it can be overwritten
    # using the configure_workflow_spec_converter.
    VERSION = "1.0"
    VERSION_KEY = "serializer_version"
    DEFAULT_JSON_ENCODER_CLS = None
    DEFAULT_JSON_DECODER_CLS = None

    @staticmethod
    def configure_workflow_spec_converter(task_spec_overrides=None, data_converter=None, version=VERSION):
        """
        This method can be used to add additional task spec converters to the default BPMN Process
        converter.

        The task specs may contain arbitrary data, though none of the default task specs use it.  We
        may disallow that in the future, so we don't recommend using this capability.

        The task spec converters also take an optional typename argument; this will be included in the
        serialized dictionaries so that the original class can restored.  The unqualified classname is
        used if none is provided.  If a class in `task_spec_overrides` conflicts with one of the
        defaults, the default will be removed and the provided one will be used instead.  If you need
        both for some reason, you'll have to instantiate the task spec converters and workflow spec
        converter yourself.

        :param task_spec_overrides: a list of task spec converter classes
        :param data_converter: an optional data converter for task spec data
        """
        if task_spec_overrides is None:
            task_spec_overrides = []

        classnames = [c.__name__ for c in task_spec_overrides]
        converters = [c(data_converter=data_converter) for c in task_spec_overrides]
        for c in DEFAULT_TASK_SPEC_CONVERTER_CLASSES:
            if c.__name__ not in classnames:
                converters.append(c(data_converter=data_converter))
        return BpmnProcessSpecConverter(converters, version)


    def __init__(self, spec_converter=None, data_converter=None, wf_class=None, version=VERSION, json_encoder_cls=DEFAULT_JSON_ENCODER_CLS, json_decoder_cls=DEFAULT_JSON_DECODER_CLS):
        """Intializes a Workflow Serializer with the given Workflow, Task and Data Converters.

        :param spec_converter: the workflow spec converter
        :param data_converter: the data converter
        :param wf_class: the workflow class
        :param json_encoder_cls: JSON encoder class to be used for dumps/dump operations
        :param json_decoder_cls: JSON decoder class to be used for loads/load operations
        """
        super().__init__()
        self.spec_converter = spec_converter if spec_converter is not None else self.configure_workflow_spec_converter()
        self.data_converter = data_converter if data_converter is not None else BpmnDataConverter()
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

    def deserialize_json(self, serialization, read_only=False, use_gzip=False):
        dct = self.__get_dict(serialization, use_gzip)
        return self.workflow_from_dict(dct, read_only)

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
        return dct

    def workflow_from_dict(self, dct, read_only=False):
        """Create a workflow based on a dictionary representation.

        :param dct: the dictionary representation
        :param read_only: optionally disable modifying the workflow

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
        workflow = self.wf_class(spec, subprocess_specs, read_only=read_only, deserializing=True)

        # Restore any unretrieve messages
        workflow.bpmn_messages = [ self.message_from_dict(msg) for msg in dct.get('bpmn_messages', []) ]

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
            subprocess = self.wf_class(subprocess_spec, {}, name=task_spec.name, parent=process, read_only=top.read_only)
            subprocess_dct = top_dct['subprocesses'].get(task_id, {})
            subprocess.data = self.data_converter.restore(subprocess_dct.pop('data'))
            subprocess.success = subprocess_dct.pop('success')
            subprocess.task_tree = self.task_tree_from_dict(subprocess_dct, subprocess_dct.pop('root'), None, subprocess, top, top_dct)
            subprocess.completed_event.connect(task_spec._on_subworkflow_completed, task)
            top_level_workflow.subprocesses[task.id] = subprocess

        for child in [ process_dct['tasks'][c] for c in task_dict['children'] ]:
            self.task_tree_from_dict(process_dct, child['id'], task, process, top, top_dct)

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
