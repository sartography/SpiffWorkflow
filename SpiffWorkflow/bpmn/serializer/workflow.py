import json
import gzip
from copy import deepcopy
from uuid import UUID

from .bpmn_converters import BpmnDataConverter

from ..workflow import BpmnWorkflow
from ..specs.SubWorkflowTask import SubWorkflowTask
from ...task import Task, TaskState

from .workflow_spec_converter import BpmnProcessSpecConverter

from .task_spec_converters import SimpleTaskConverter, StartTaskConverter, EndJoinConverter, LoopResetTaskConverter
from .task_spec_converters import NoneTaskConverter, UserTaskConverter, ManualTaskConverter, ScriptTaskConverter
from .task_spec_converters import CallActivityTaskConverter, TransactionSubprocessTaskConverter
from .task_spec_converters import StartEventConverter, EndEventConverter
from .task_spec_converters import IntermediateCatchEventConverter, IntermediateThrowEventConverter
from .task_spec_converters import BoundaryEventConverter, BoundaryEventParentConverter
from .task_spec_converters import ParallelGatewayConverter, ExclusiveGatewayConverter, InclusiveGatewayConverter

DEFAULT_TASK_SPEC_CONVERTER_CLASSES = [
    SimpleTaskConverter, StartTaskConverter, EndJoinConverter, LoopResetTaskConverter,
    NoneTaskConverter, UserTaskConverter, ManualTaskConverter, ScriptTaskConverter,
    CallActivityTaskConverter, TransactionSubprocessTaskConverter,
    StartEventConverter, EndEventConverter,
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


    def __init__(self, spec_converter=None, data_converter=None, wf_class=None, version=VERSION):
        """Intializes a Workflow Serializer with the given Workflow, Task and Data Converters.

        :param spec_converter: the workflow spec converter
        :param data_converter: the data converter
        :param wf_class: the workflow class
        """
        super().__init__()
        self.spec_converter = spec_converter if spec_converter is not None else self.configure_workflow_spec_converter()
        self.data_converter = data_converter if data_converter is not None else BpmnDataConverter()
        self.wf_class = wf_class if wf_class is not None else BpmnWorkflow
        self.VERSION = version

    def serialize_json(self, workflow, use_gzip=False):
        """Serialize the dictionary representation of the workflow to JSON.

        :param workflow: the workflow to serialize

        Returns:
            a JSON dump of the dictionary representation
        """
        dct = self.workflow_to_dict(workflow)
        dct['serializer_version'] = self.VERSION
        json_str = json.dumps(dct)
        return gzip.compress(json_str.encode('utf-8')) if use_gzip else json_str

    def deserialize_json(self, serialization, read_only=False, use_gzip=False):
        dct = json.loads(gzip.decompress(serialization)) if use_gzip else json.loads(serialization)
        version = dct.pop('serializer_version')
        return self.workflow_from_dict(dct, read_only)

    def get_version(self, serialization):
        try:
            dct = json.loads(serialization)
            if 'serializer_version' in dct:
                return dct['serializer_version']
        except:  # Don't bail out trying to get a version, just return none.
            return None

    def workflow_to_dict(self, workflow):
        """Return a JSON-serializable dictionary representation of the workflow.

        :param workflow: the workflow

        Returns:
            a dictionary representation of the workflow
        """
        return {
            'spec': self.spec_converter.convert(workflow.spec),
            'data': self.data_converter.convert(workflow.data),
            'last_task': str(workflow.last_task.id) if workflow.last_task is not None else None,
            'success': workflow.success,
            'tasks': self.task_tree_to_dict(workflow.task_tree),
            'root': str(workflow.task_tree.id),
            'subprocess_specs': dict(
                (name, self.spec_converter.convert(spec)) for name, spec in workflow.subprocess_specs.items()
            ),
            'subprocesses': dict((
                str(task_id), [str(task.id) for task in sp.get_tasks() if task in workflow.get_tasks()]
            ) for task_id, sp in workflow.subprocesses.items()),
        }

    def workflow_from_dict(self, dct, read_only=False):
        """Create a workflow based on a dictionary representation.

        :param dct: the dictionary representation
        :param read_only: optionally disable modifying the workflow

        Returns:
            a BPMN Workflow object
        """
        dct_copy = deepcopy(dct)

        # First, we'll restore the specs for all the subprocesses
        for name, wf_dct in dct_copy['subprocess_specs'].items():
            dct_copy['subprocess_specs'][name] = self.spec_converter.restore(wf_dct)

        # Restore the top level spec.
        spec = self.spec_converter.restore(dct_copy.pop('spec'))

        workflow = self.wf_class(spec, dct_copy['subprocess_specs'], read_only=read_only)
        workflow.data = self.data_converter.restore(dct_copy.pop('data'))
        workflow.success = dct_copy.pop('success')
        
        root = dct_copy.pop('root')
        workflow.task_tree = self.task_tree_from_dict(dct_copy, root, None, workflow, read_only)
        workflow.subprocesses = dct_copy['subprocesses']
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

        task = Task(workflow, task_spec, parent)
        task.id = UUID(dct['id'])
        task.state = TaskState(dct['state'])
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

    def task_tree_from_dict(self, dct, task_id, parent, workflow, read_only):

        task_dict = dct['tasks'][task_id]
        task_spec = workflow.spec.task_specs[task_dict['task_spec']]
        task = self.task_from_dict(task_dict, workflow, task_spec, parent)
        if task_id == dct['last_task']:
            workflow.last_task = task

        children = [dct['tasks'][c] for c in task_dict['children']]
        subtasks = dct['subprocesses'].get(str(task_id), [])

        if isinstance(task_spec, SubWorkflowTask) and len(subtasks) > 0:
            subprocess_spec = dct['subprocess_specs'][task_spec.spec]           
            subprocess = self.wf_class(subprocess_spec, name=task_spec.name, parent=workflow, read_only=read_only)
            root = subtasks[0]
            subprocess.task_tree = self.task_tree_from_dict(dct, root, task, subprocess, read_only)
            subprocess.completed_event.connect(task_spec._on_subworkflow_completed, task)
            dct['subprocesses'].pop(str(task.id))
            dct['subprocesses'][task.id] = subprocess

        for child in [ c for c in children if c['id'] not in subtasks ]:
            self.task_tree_from_dict(dct, child['id'], task, workflow, read_only)

        return task
