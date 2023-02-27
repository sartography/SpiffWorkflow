from SpiffWorkflow.bpmn.serializer.helpers.spec import TaskSpecConverter
from SpiffWorkflow.bpmn.serializer.task_spec import MultiInstanceTaskConverter

from SpiffWorkflow.spiff.specs.none_task import NoneTask
from SpiffWorkflow.spiff.specs.manual_task import ManualTask
from SpiffWorkflow.spiff.specs.user_task import UserTask
from SpiffWorkflow.spiff.specs.script_task import ScriptTask
from SpiffWorkflow.spiff.specs.service_task import ServiceTask
from SpiffWorkflow.spiff.specs.subworkflow_task import SubWorkflowTask, TransactionSubprocess, CallActivity
from SpiffWorkflow.spiff.specs.events.event_types import SendTask, ReceiveTask
from SpiffWorkflow.spiff.specs.multiinstance_task import StandardLoopTask, ParallelMultiInstanceTask, SequentialMultiInstanceTask


class SpiffBpmnTaskConverter(TaskSpecConverter):

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        dct['prescript'] = spec.prescript
        dct['postscript'] = spec.postscript
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class NoneTaskConverter(SpiffBpmnTaskConverter):
    def __init__(self, registry):
        super().__init__(NoneTask, registry)


class ManualTaskConverter(SpiffBpmnTaskConverter):
    def __init__(self, registry):
        super().__init__(ManualTask, registry)


class UserTaskConverter(SpiffBpmnTaskConverter):
    def __init__(self, registry):
        super().__init__(UserTask, registry)


class SendTaskConverter(SpiffBpmnTaskConverter):

    def __init__(self, registry, typename=None):
        super().__init__(SendTask, registry, typename)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['event_definition'] = self.registry.convert(spec.event_definition)
        return dct

    def from_dict(self, dct):
        dct['event_definition'] = self.registry.restore(dct['event_definition'])
        return super().from_dict(dct)


class ReceiveTaskConverter(SpiffBpmnTaskConverter):
    def __init__(self, registry, typename=None):
        super().__init__(ReceiveTask, registry, typename)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['event_definition'] = self.registry.convert(spec.event_definition)
        return dct

    def from_dict(self, dct):
        dct['event_definition'] = self.registry.restore(dct['event_definition'])
        return super().from_dict(dct)


class ScriptTaskConverter(SpiffBpmnTaskConverter):
    def __init__(self, registry):
        super().__init__(ScriptTask, registry)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['script'] = spec.script
        return dct


class ServiceTaskConverter(SpiffBpmnTaskConverter):
    def __init__(self, registry):
        super().__init__(ServiceTask, registry)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['operation_name'] = spec.operation_name
        dct['operation_params'] = spec.operation_params
        dct['result_variable'] = spec.result_variable
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class SubWorkflowTaskConverter(SpiffBpmnTaskConverter):

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct.update(self.get_subworkflow_attributes(spec))
        return dct

    def from_dict(self, dct):
        dct['subworkflow_spec'] = dct.pop('spec')
        return super().task_spec_from_dict(dct)

class SubprocessTaskConverter(SubWorkflowTaskConverter):
    def __init__(self, registry):
        super().__init__(SubWorkflowTask, registry)

class TransactionSubprocessConverter(SubWorkflowTaskConverter):
    def __init__(self, registry):
        super().__init__(TransactionSubprocess, registry)

class CallActivityTaskConverter(SubWorkflowTaskConverter):
    def __init__(self, registry):
        super().__init__(CallActivity, registry)


class StandardLoopTaskConverter(SpiffBpmnTaskConverter):

    def __init__(self, registry):
        super().__init__(StandardLoopTask, registry)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        dct.update(self.get_standard_loop_attributes(spec))
        return dct


class SpiffMultiInstanceConverter(MultiInstanceTaskConverter, SpiffBpmnTaskConverter):

    def to_dict(self, spec):
        dct = MultiInstanceTaskConverter.to_dict(self, spec)
        dct.update(SpiffBpmnTaskConverter.to_dict(self, spec))
        return dct

class ParallelMultiInstanceTaskConverter(SpiffMultiInstanceConverter):
    def __init__(self, registry):
        super().__init__(ParallelMultiInstanceTask, registry)

class SequentialMultiInstanceTaskConverter(SpiffMultiInstanceConverter):
    def __init__(self, registry):
        super().__init__(SequentialMultiInstanceTask, registry)