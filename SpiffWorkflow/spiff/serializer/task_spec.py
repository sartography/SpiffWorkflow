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

from SpiffWorkflow.bpmn.serializer.helpers.spec import TaskSpecConverter
from SpiffWorkflow.bpmn.serializer.default.task_spec import MultiInstanceTaskConverter
from SpiffWorkflow.dmn.serializer.task_spec import BaseBusinessRuleTaskConverter

from SpiffWorkflow.spiff.specs.defaults import (
    NoneTask,
    ManualTask,
    UserTask,
    ScriptTask,
    SendTask,
    ReceiveTask,
    StandardLoopTask,
    ParallelMultiInstanceTask,
    SequentialMultiInstanceTask,
    BusinessRuleTask,
    SubWorkflowTask,
    CallActivity,
    TransactionSubprocess,
    ServiceTask
)

class SpiffBpmnTaskConverter(TaskSpecConverter):

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct['prescript'] = spec.prescript
        dct['postscript'] = spec.postscript
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class BusinessRuleTaskConverter(BaseBusinessRuleTaskConverter, SpiffBpmnTaskConverter):

    def to_dict(self, spec):
        dct = BaseBusinessRuleTaskConverter.to_dict(self, spec)
        dct.update(SpiffBpmnTaskConverter.to_dict(self, spec))
        return dct


class SendReceiveTaskConverter(SpiffBpmnTaskConverter):

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['event_definition'] = self.registry.convert(spec.event_definition)
        return dct

    def from_dict(self, dct):
        dct['event_definition'] = self.registry.restore(dct['event_definition'])
        return super().from_dict(dct)


class ScriptTaskConverter(SpiffBpmnTaskConverter):

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['script'] = spec.script
        return dct


class UserTaskConverter(SpiffBpmnTaskConverter):

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['variable'] = spec.variable
        return dct


class ServiceTaskConverter(SpiffBpmnTaskConverter):

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


class StandardLoopTaskConverter(SpiffBpmnTaskConverter):

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct.update(self.get_standard_loop_attributes(spec))
        return dct


class SpiffMultiInstanceConverter(MultiInstanceTaskConverter, SpiffBpmnTaskConverter):

    def to_dict(self, spec):
        dct = MultiInstanceTaskConverter.to_dict(self, spec)
        dct.update(SpiffBpmnTaskConverter.to_dict(self, spec))
        return dct
