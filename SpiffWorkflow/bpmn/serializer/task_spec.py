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

from SpiffWorkflow.bpmn.specs.control import BpmnStartTask, _EndJoin, _BoundaryEventParent, SimpleBpmnTask
from SpiffWorkflow.bpmn.specs.bpmn_task_spec import _BpmnCondition
from SpiffWorkflow.bpmn.specs.defaults import (
    UserTask,
    ManualTask,
    NoneTask,
    ScriptTask,
    ExclusiveGateway,
    InclusiveGateway,
    ParallelGateway,
    StandardLoopTask,
    SequentialMultiInstanceTask,
    ParallelMultiInstanceTask,
    CallActivity,
    TransactionSubprocess,
    SubWorkflowTask,
    StartEvent,
    EndEvent,
    IntermediateCatchEvent,
    IntermediateThrowEvent,
    BoundaryEvent,
    EventBasedGateway,
    SendTask,
    ReceiveTask,
)

from .helpers.spec import TaskSpecConverter


class BpmnTaskSpecConverter(TaskSpecConverter):

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class SimpleBpmnTaskConverter(BpmnTaskSpecConverter):
    def __init__(self, registry):
        super().__init__(SimpleBpmnTask, registry)

class BpmnStartTaskConverter(BpmnTaskSpecConverter):
    def __init__(self, registry):
        super().__init__(BpmnStartTask, registry)

class EndJoinConverter(BpmnTaskSpecConverter):
    def __init__(self, registry):
        super().__init__(_EndJoin, registry)



class NoneTaskConverter(BpmnTaskSpecConverter):
    def __init__(self, registry):
        super().__init__(NoneTask, registry)


class UserTaskConverter(BpmnTaskSpecConverter):
    def __init__(self, registry):
        super().__init__(UserTask, registry)


class ManualTaskConverter(BpmnTaskSpecConverter):
    def __init__(self, registry):
        super().__init__(ManualTask, registry)


class ScriptTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, registry):
        super().__init__(ScriptTask, registry)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct['script'] = spec.script
        return dct


class StandardLoopTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, registry):
        super().__init__(StandardLoopTask, registry)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_standard_loop_attributes(spec))
        return dct


class MultiInstanceTaskConverter(BpmnTaskSpecConverter):

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct['task_spec'] = spec.task_spec
        dct['cardinality'] = spec.cardinality
        dct['data_input'] = self.registry.convert(spec.data_input)
        dct['data_output'] = self.registry.convert(spec.data_output)
        dct['input_item'] = self.registry.convert(spec.input_item)
        dct['output_item'] = self.registry.convert(spec.output_item)
        dct['condition'] = spec.condition
        return dct

    def from_dict(self, dct):
        dct['data_input'] = self.registry.restore(dct['data_input'])
        dct['data_output'] = self.registry.restore(dct['data_output'])
        dct['input_item'] = self.registry.restore(dct['input_item'])
        dct['output_item'] = self.registry.restore(dct['output_item'])
        return self.task_spec_from_dict(dct)


class ParallelMultiInstanceTaskConverter(MultiInstanceTaskConverter):
    def __init__(self, registry):
        super().__init__(ParallelMultiInstanceTask, registry)

class SequentialMultiInstanceTaskConverter(MultiInstanceTaskConverter):
    def __init__(self, registry):
        super().__init__(SequentialMultiInstanceTask, registry)


class BoundaryEventParentConverter(BpmnTaskSpecConverter):

    def __init__(self, registry):
        super().__init__(_BoundaryEventParent, registry)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['main_child_task_spec'] = spec.main_child_task_spec.name
        return dct


class SubWorkflowConverter(BpmnTaskSpecConverter):

    def __init__(self, cls, registry):
        super().__init__(cls, registry)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct.update(self.get_subworkflow_attributes(spec))
        return dct

    def from_dict(self, dct):
        dct['subworkflow_spec'] = dct.pop('spec')
        return self.task_spec_from_dict(dct)

class SubprocessTaskConverter(SubWorkflowConverter):
    def __init__(self, registry):
        super().__init__(SubWorkflowTask, registry)

class CallActivityTaskConverter(SubWorkflowConverter):
    def __init__(self, registry):
        super().__init__(CallActivity, registry)

class TransactionSubprocessTaskConverter(SubWorkflowConverter):
    def __init__(self, registry):
        super().__init__(TransactionSubprocess, registry)


class ConditionalGatewayConverter(BpmnTaskSpecConverter):

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['cond_task_specs'] = [ self.bpmn_condition_to_dict(cond) for cond in spec.cond_task_specs ]
        dct['choice'] = spec.choice
        return dct

    def from_dict(self, dct):
        conditions = dct.pop('cond_task_specs')
        spec = self.task_spec_from_dict(dct)
        spec.cond_task_specs = [ self.bpmn_condition_from_dict(cond) for cond in conditions ]
        return spec

    def bpmn_condition_from_dict(self, dct):
        return (_BpmnCondition(dct['condition']) if dct['condition'] is not None else None, dct['task_spec'])

    def bpmn_condition_to_dict(self, condition):
        expr, task_spec = condition
        return {
            'condition': expr.args[0] if expr is not None else None,
            'task_spec': task_spec
        }


class ExclusiveGatewayConverter(ConditionalGatewayConverter):

    def __init__(self, registry):
        super().__init__(ExclusiveGateway, registry)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['default_task_spec'] = spec.default_task_spec
        return dct

    def from_dict(self, dct):
        default_task_spec = dct.pop('default_task_spec')
        spec = super().from_dict(dct)
        spec.default_task_spec = default_task_spec
        return spec


class InclusiveGatewayConverter(ConditionalGatewayConverter):
    def __init__(self, registry):
        super().__init__(InclusiveGateway, registry)


class ParallelGatewayConverter(BpmnTaskSpecConverter):

    def __init__(self, registry):
        super().__init__(ParallelGateway, registry)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct.update(self.get_join_attributes(spec))
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class EventConverter(BpmnTaskSpecConverter):

    def __init__(self, spec_class, registry):
        super().__init__(spec_class, registry)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['event_definition'] = self.registry.convert(spec.event_definition)
        return dct

    def from_dict(self, dct):
        dct['event_definition'] = self.registry.restore(dct['event_definition'])
        return self.task_spec_from_dict(dct)


class StartEventConverter(EventConverter):
    def __init__(self, registry):
        super().__init__(StartEvent, registry)


class EndEventConverter(EventConverter):
    def __init__(self, registry):
        super().__init__(EndEvent, registry)


class IntermediateCatchEventConverter(EventConverter):
    def __init__(self, registry):
        super().__init__(IntermediateCatchEvent, registry)


class ReceiveTaskConverter(EventConverter):
    def __init__(self, registry):
        super().__init__(ReceiveTask, registry)


class IntermediateThrowEventConverter(EventConverter):
    def __init__(self, registry):
        super().__init__(IntermediateThrowEvent, registry)


class SendTaskConverter(EventConverter):
    def __init__(self, registry):
        super().__init__(SendTask, registry)


class BoundaryEventConverter(EventConverter):

    def __init__(self, registry):
        super().__init__(BoundaryEvent, registry)

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['cancel_activity'] = spec.cancel_activity
        return dct


class EventBasedGatewayConverter(EventConverter):
    def __init__(self, registry):
        super().__init__(EventBasedGateway, registry)


DEFAULT_TASK_SPEC_CONVERTER_CLASSES = [
    SimpleBpmnTaskConverter,
    BpmnStartTaskConverter,
    EndJoinConverter,
    NoneTaskConverter,
    UserTaskConverter,
    ManualTaskConverter,
    ScriptTaskConverter,
    StandardLoopTaskConverter,
    ParallelMultiInstanceTaskConverter,
    SequentialMultiInstanceTaskConverter,
    SubprocessTaskConverter,
    CallActivityTaskConverter,
    TransactionSubprocessTaskConverter,
    StartEventConverter,
    EndEventConverter, 
    SendTaskConverter,
    ReceiveTaskConverter,
    IntermediateCatchEventConverter,
    IntermediateThrowEventConverter,
    EventBasedGatewayConverter,
    BoundaryEventConverter,
    BoundaryEventParentConverter,
    ParallelGatewayConverter,
    ExclusiveGatewayConverter,
    InclusiveGatewayConverter,
]