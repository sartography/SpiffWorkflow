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

from SpiffWorkflow.bpmn.specs.mixins import (
    ManualTaskMixin,
    NoneTaskMixin,
    ScriptTaskMixin,
    SubWorkflowTaskMixin,
    CallActivityMixin,
    TransactionSubprocessMixin,
    StandardLoopTaskMixin,
    ParallelMultiInstanceTaskMixin,
    SequentialMultiInstanceTaskMixin,
    SendTaskMixin,
    ReceiveTaskMixin,
)
from SpiffWorkflow.dmn.specs import BusinessRuleTaskMixin

from .mixins.service_task import ServiceTask as ServiceTaskMixin
from .mixins.user_task import UserTask as UserTaskMixin
from .spiff_task import SpiffBpmnTask


class UserTask(UserTaskMixin, SpiffBpmnTask):
    pass

class ManualTask(ManualTaskMixin, SpiffBpmnTask):
    pass

class NoneTask(NoneTaskMixin, SpiffBpmnTask):
    pass

class ScriptTask(ScriptTaskMixin, SpiffBpmnTask):
    pass

class SendTask(SendTaskMixin, SpiffBpmnTask):
    pass

class ReceiveTask(ReceiveTaskMixin, SpiffBpmnTask):
    pass

class StandardLoopTask(StandardLoopTaskMixin, SpiffBpmnTask):
    pass

class ParallelMultiInstanceTask(ParallelMultiInstanceTaskMixin, SpiffBpmnTask):
    pass

class SequentialMultiInstanceTask(SequentialMultiInstanceTaskMixin, SpiffBpmnTask):
    pass

class BusinessRuleTask(BusinessRuleTaskMixin, SpiffBpmnTask):
    pass

class SubWorkflowTask(SubWorkflowTaskMixin, SpiffBpmnTask):
    pass

class CallActivity(CallActivityMixin, SpiffBpmnTask):
    pass

class TransactionSubprocess(TransactionSubprocessMixin, SpiffBpmnTask):
    pass

class ServiceTask(ServiceTaskMixin, SpiffBpmnTask):
    pass
