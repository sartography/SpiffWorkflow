from uuid import UUID

from .bpmn_converters import BpmnTaskSpecConverter

from ...specs import StartTask
from ...specs.Simple import Simple
from ...specs.LoopResetTask import LoopResetTask

from ..specs.BpmnProcessSpec import _EndJoin
from ..specs.BpmnSpecMixin import _BpmnCondition

from ..specs.NoneTask import NoneTask
from ..specs.UserTask import UserTask
from ..specs.ManualTask import ManualTask
from ..specs.ScriptTask import ScriptTask
from ..specs.SubWorkflowTask import CallActivity, TransactionSubprocess

from ..specs.ExclusiveGateway import ExclusiveGateway
from ..specs.InclusiveGateway import InclusiveGateway
from ..specs.ParallelGateway import ParallelGateway

from ..specs.events import StartEvent, EndEvent, BoundaryEvent, IntermediateCatchEvent, IntermediateThrowEvent
from ..specs.events.IntermediateEvent import _BoundaryEventParent, SendTask, ReceiveTask

from ..workflow import BpmnWorkflow


class SimpleTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(Simple, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class StartTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(StartTask, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)

class LoopResetTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(LoopResetTask, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        # Maybe I should add this to the base task converter, but I'm trying to keep it free of
        # anything but task related conversions
        dct['destination_id'] = str(spec.destination_id)
        dct['destination_spec_name'] = spec.destination_spec_name
        return dct

    def from_dict(self, dct):
        spec = self.task_spec_from_dict(dct)
        spec.destination_id = UUID(spec.destination_id)
        return spec

class EndJoinConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(_EndJoin, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class NoneTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(NoneTask, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class UserTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(UserTask, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class ManualTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(ManualTask, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class ScriptTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(ScriptTask, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        dct['script'] = spec.script
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class CallActivityTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(CallActivity, data_converter, typename)
        self.wf_class = BpmnWorkflow

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        dct.update(self.get_subworkflow_attributes(spec))
        return dct

    def from_dict(self, dct):
        dct['subworkflow_spec'] = dct.pop('spec')
        return self.task_spec_from_dict(dct)


class TransactionSubprocessTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(TransactionSubprocess, data_converter, typename)
        self.wf_class = BpmnWorkflow

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        dct.update(self.get_subworkflow_attributes(spec))
        return dct

    def from_dict(self, dct):
        dct['subworkflow_spec'] = dct.pop('spec')
        return self.task_spec_from_dict(dct)


class ExclusiveGatewayConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(ExclusiveGateway, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        dct['default_task_spec'] = spec.default_task_spec
        dct['cond_task_specs'] = [ self.bpmn_condition_to_dict(cond) for cond in spec.cond_task_specs ]
        dct['choice'] = spec.choice
        return dct

    def from_dict(self, dct):
        conditions = dct.pop('cond_task_specs')
        default_task_spec = dct.pop('default_task_spec')
        spec = self.task_spec_from_dict(dct)
        spec.cond_task_specs = [ self.bpmn_condition_from_dict(cond) for cond in conditions ]
        spec.default_task_spec = default_task_spec
        return spec

    def bpmn_condition_from_dict(self, dct):
        return (_BpmnCondition(dct['condition']), dct['task_spec'])

    def bpmn_condition_to_dict(self, condition):

        expr, task_spec = condition
        return {
            'condition': expr.args[0],
            'task_spec': task_spec
        }

class InclusiveGatewayConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(InclusiveGateway, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        dct.update(self.get_join_attributes(spec))
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class ParallelGatewayConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(ParallelGateway, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        dct.update(self.get_join_attributes(spec))
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class EventConverter(BpmnTaskSpecConverter):

    def __init__(self, spec_class, data_converter, typename):
        super().__init__(spec_class, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        dct['event_definition'] = self.convert(spec.event_definition)
        return dct

    def from_dict(self, dct):
        dct['event_definition'] = self.restore(dct['event_definition'])
        return self.task_spec_from_dict(dct)


class StartEventConverter(EventConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(StartEvent, data_converter, typename)


class EndEventConverter(EventConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(EndEvent, data_converter, typename)


class IntermediateCatchEventConverter(EventConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(IntermediateCatchEvent, data_converter, typename)


class ReceiveTaskConverter(EventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(ReceiveTask, data_converter, typename)


class IntermediateThrowEventConverter(EventConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(IntermediateThrowEvent, data_converter, typename)


class SendTaskConverter(EventConverter):
    def __init__(self, data_converter=None, typename=None):
        super().__init__(SendTask, data_converter, typename)


class BoundaryEventConverter(EventConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(BoundaryEvent, data_converter, typename)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['cancel_activity'] = spec.cancel_activity
        return dct


class BoundaryEventParentConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(_BoundaryEventParent, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        dct['main_child_task_spec'] = spec.main_child_task_spec.name
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)
