import json
from copy import deepcopy
from uuid import UUID

from .workflow_spec_converter import BpmnProcessSpecConverter
from .bpmn_converters import BpmnDataConverter

from .task_spec_converters import SimpleTaskConverter, StartTaskConverter, EndJoinConverter, LoopResetTaskConverter
from .task_spec_converters import NoneTaskConverter, UserTaskConverter, ManualTaskConverter, ScriptTaskConverter
from .task_spec_converters import CallActivityTaskConverter, TransactionSubprocessTaskConverter
from .task_spec_converters import StartEventConverter, EndEventConverter
from .task_spec_converters import IntermediateCatchEventConverter, IntermediateThrowEventConverter
from .task_spec_converters import BoundaryEventConverter, BoundaryEventParentConverter
from .task_spec_converters import ParallelGatewayConverter, ExclusiveGatewayConverter, InclusiveGatewayConverter

from ..workflow import BpmnWorkflow
from ..specs.SubWorkflowTask import SubWorkflowTask
from ...task import Task

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
    class and a Data Converter class.  The Workflow Spec Converter is configured with Task Spec Converter
    classes and an optional Data Converter class.  
    
    The goal is to provide modular serialization capabilities.

    Serialization occurs in two phases: the first is to convert everything in the workflow to a
    dictionary containins only JSON-serializable objects and the second is dumping to JSON.

    This means that you can call the `workflow_to_dict` or `workflow_from_dict` methods separately from
    conversion to JSON for further manipulation of the state, or selective serialization of only certain
    parts of the workflow more conveniently.  You can of course call methods from the Workflow Spec and 
    Data Converters via the `spec_converter` and `data_converter` attributes as well to bypass the
    overhead of converting or restoring the entire thing.

    The Workflow is at the top level and relies on different Converters for its Spec and Data.  
    
    Task Spec conversion is handled through Workflow Spec converter.

    The Task Spec converters optionally rely on a Data Converter.  BPMN task specs would typically not
    have data attached to them, but the base Spiff tasks allow for arbitrary data.  We recommend not
    doing this, as we may disallow it in the future.
    
    This results in a certain amount of complexity, so several factory methods are provided for creating 
    serializers based on common use cases.
    """

    VERSION = 1.0

    @classmethod
    def default(cls):
        """
        Creates a Workflow Serializer using the default task spec converters (listed above and defined in 
        `task_spec_converters`), the `BmpnProcessSpecConverter` (defined in `workflow_spec_converter`),
        and the default data converter (`BpmnataConverter`, defined in `bpmn_converters`).

        If you have not implemented any custom tasks and your workflow/task data contains only JSON-
        serializable objects, you can call this method in lieu of configuring everything yourself.
        """
        data_converter = BpmnDataConverter()
        task_spec_converters = map(lambda c: c(), DEFAULT_TASK_SPEC_CONVERTER_CLASSES)       
        spec_converter = BpmnProcessSpecConverter(task_spec_converters)
        return cls(BpmnWorkflow, spec_converter, data_converter)

    @classmethod
    def with_custom_data(cls, data_converter):
        """
        Creates a Workflow Serializer using the default BPMN Converters, but replaces the Data Converter
        with a custom class.

        If you have not implemented any custom tasks but your workflow/task data contains non-JSON-
        serializable objects, you should extend or replace the Data Converter with one that can handle
        your use case and use this method to create a serializer.

        Note that the data converter will only be passed to the Workflow Serializer *not* the
        Task Spec Converter.
        """
        task_spec_converters = map(lambda c: c(), DEFAULT_TASK_SPEC_CONVERTER_CLASSES)       
        spec_converter = BpmnProcessSpecConverter(task_spec_converters)
        return cls(BpmnWorkflow, spec_converter, data_converter)

    @classmethod
    def add_task_spec_converter_classes(cls, converter_classes, data_converter=None):
        """Creates a Workflow Serializer with additional Task Spec Converters and an optional
        custom Data Converter.

        If you have implemented any custom task spec classes, then you can provide converters for
        them to this method and they will be added along with the stanard Task Spec converters.

        If no Data Converter is given, the default BpmnDataConverter will be used.

        Note that the data converter will only be passed to the Workflow Serializer *not* the
        Task Spec Converter.
        """
        if data_converter is None:
            data_converter = BpmnDataConverter()
        task_spec_converters = map(lambda c: c(), DEFAULT_TASK_SPEC_CONVERTER_CLASSES + converter_classes)
        spec_converter = BpmnProcessSpecConverter(task_spec_converters)
        return cls(BpmnWorkflow, spec_converter, data_converter)

    def __init__(self, wf_class, spec_converter, data_converter):
        """Intializes a Workflow Serializer with the given Workflow, Task and Data Converters.

        :param wf_class: the workflow class
        :param spec_converter: the workflow spec converter
        :param data_converter: the data converter
        """
        super().__init__()
        self.wf_class = wf_class
        self.spec_converter = spec_converter
        self.data_converter = data_converter

    def serialize_json(self, workflow):
        """Serialize the dictionary representation of the workflow to JSON.
        
        :param workflow: the workflow to serialize

        Returns:
            a JSON dump of the dictionary representation
        """
        dct = self.workflow_to_dict(workflow)
        dct['serializer_version'] = self.VERSION
        return json.dumps(dct)

    def deserialize_json(self, serialization, read_only=False):
        dct = json.loads(serialization)
        version = dct.pop('serializer_version')
        return self.workflow_from_dict(dct, read_only)

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
        }

    def workflow_from_dict(self, dct, read_only=False):
        """Create a workflow based on a dictionary representation.

        :param dct: the dictionary representation
        :param read_only: optionally disable modifying the workflow

        Returns:
            a BPMN Workflow object
        """
        dct_copy = deepcopy(dct)
        spec = self.spec_converter.restore(dct_copy.pop('spec'))
        workflow = self.wf_class(spec, read_only=read_only)
        workflow.data = self.data_converter.restore(dct_copy.pop('data'))
        workflow.success = dct_copy.pop('success')

        root = dct_copy.pop('root')
        workflow.task_tree = self.task_tree_from_dict(dct_copy, root, None, workflow, read_only)
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
        task.state = dct['state']
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

        children = [ dct['tasks'][child] for child in task_dict['children'] ]

        if isinstance(task_spec, SubWorkflowTask) and task_spec.sub_workflow is not None:
            task_spec.sub_workflow = self.wf_class(
                task_spec.spec, name=task_spec.sub_workflow, parent=workflow, read_only=read_only)
            root = [ c for c in children if c['workflow_name'] == task_spec.sub_workflow.name ][0]
            task_spec.sub_workflow.task_tree = self.task_tree_from_dict(
                dct, root['id'], task, task_spec.sub_workflow, read_only)
            task_spec.sub_workflow.completed_event.connect(task_spec._on_subworkflow_completed, task)

        for child in [ c for c in children if c['workflow_name'] == workflow.name ]:
            self.task_tree_from_dict(dct, child['id'], task, workflow, read_only)

        return task