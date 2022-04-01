import json
from uuid import UUID

from .task_spec_converters import SimpleTaskConverter, StartTaskConverter, EndJoinConverter, LoopResetTaskConverter
from .task_spec_converters import NoneTaskConverter, UserTaskConverter, ManualTaskConverter, ScriptTaskConverter
from .task_spec_converters import CallActivityTaskConverter, TransactionSubprocessTaskConverter
from .task_spec_converters import StartEventConverter, EndEventConverter
from .task_spec_converters import IntermediateCatchEventConverter, IntermediateThrowEventConverter
from .task_spec_converters import BoundaryEventConverter, BoundaryEventParentConverter
from .task_spec_converters import ParallelGatewayConverter, ExclusiveGatewayConverter, InclusiveGatewayConverter

from .bpmn_converters import BpmnDataConverter, BpmnWorkflowSpecConverter

from ..workflow import BpmnWorkflow
from ..specs.BpmnProcessSpec import BpmnProcessSpec
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

    VERSION = 1.0

    @classmethod
    def default(cls):
        data_converter = BpmnDataConverter()
        task_spec_converters = map(lambda c: c(), DEFAULT_TASK_SPEC_CONVERTER_CLASSES)       
        spec_converter = BpmnWorkflowSpecConverter(BpmnProcessSpec, task_spec_converters)
        return cls(BpmnWorkflow, spec_converter, data_converter)

    @classmethod
    def with_custom_data(cls, data_converter):
        task_spec_converters = map(lambda c: c(), DEFAULT_TASK_SPEC_CONVERTER_CLASSES)       
        spec_converter = BpmnWorkflowSpecConverter(BpmnProcessSpec, task_spec_converters)
        return cls(BpmnWorkflow, spec_converter, data_converter)

    @classmethod
    def add_task_spec_converter_classes(cls, converter_classes, data_converter=None):
        if data_converter is None:
            data_converter = BpmnDataConverter()
        task_spec_converters = map(lambda c: c(), DEFAULT_TASK_SPEC_CONVERTER_CLASSES + converter_classes)
        spec_converter = BpmnWorkflowSpecConverter(BpmnProcessSpec, task_spec_converters)
        return cls(BpmnWorkflow, spec_converter, data_converter)

    def __init__(self, wf_class, spec_converter, data_converter):

        super().__init__()
        self.wf_class = wf_class
        self.spec_converter = spec_converter
        self.data_converter = data_converter

    def serialize_json(self, workflow):
        dct = self.workflow_to_dict(workflow)
        dct['serializer_version'] = self.VERSION
        return json.dumps(dct)

    def deserialize_json(self, serialization, read_only=False):
        dct = json.loads(serialization)
        version = dct.pop('serializer_version')
        return self.workflow_from_dict(dct, read_only)

    def workflow_to_dict(self, workflow):

        return {
            'spec': self.spec_converter.convert(workflow.spec),
            'data': self.data_converter.convert(workflow.data),
            'last_task': str(workflow.last_task.id) if workflow.last_task is not None else None,
            'success': workflow.success,
            'tasks': self.task_tree_to_dict(workflow.task_tree),
            'root': str(workflow.task_tree.id),
        }

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

    def task_tree_to_dict(self, root):

        tasks = { }
        def add_task(task):
            dct = self.task_to_dict(task)
            tasks[dct['id']] = dct
            for child in task.children:
                add_task(child)

        add_task(root)
        return tasks

    def workflow_from_dict(self, dct, read_only):

        spec = self.spec_converter.restore(dct.pop('spec'))
        workflow = self.wf_class(spec, read_only=read_only)
        workflow.data = self.data_converter.restore(dct.pop('data'))
        workflow.success = dct.pop('success')

        root = dct.pop('root')
        workflow.task_tree = self.task_tree_from_dict(dct, root, None, workflow, read_only)
        return workflow

    def task_from_dict(self, dct, workflow, task_spec, parent):

        task = Task(workflow, task_spec, parent)
        task.id = UUID(dct['id'])
        task.state = dct['state']
        task.last_state_change = dct['last_state_change']
        task.triggered = dct['triggered']
        task.internal_data = self.data_converter.restore(dct['internal_data'])
        task.data = self.data_converter.restore(dct['data'])
        return task

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