# Copyright (C) 2012 Matthew Hampton, 2024 Sartography
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

from .bpmn_spec_mixin import BpmnSpecMixin
from .user_task import UserTask as UserTaskMixin
from .manual_task import ManualTask as ManualTaskMixin
from .none_task import NoneTask as NoneTaskMixin
from .script_task import ScriptTask as ScriptTaskMixin
from .service_task import ServiceTask as ServiceTaskMixin
from .parallel_gateway import ParallelGateway as ParallelGatewayMixin
from .exclusive_gateway import ExclusiveGateway as ExclusiveGatewayMixin
from .inclusive_gateway import InclusiveGateway as InclusiveGatewayMixin
from .multiinstance_task import (
    StandardLoopTask as StandardLoopTaskMixin,
    ParallelMultiInstanceTask as ParallelMultiInstanceTaskMixin,
    SequentialMultiInstanceTask as SequentialMultiInstanceTaskMixin,
)
from .subworkflow_task import (
    SubWorkflowTask as SubWorkflowTaskMixin,
    CallActivity as CallActivityMixin,
    TransactionSubprocess as TransactionSubprocessMixin,
)

from .events.start_event import StartEvent as StartEventMixin
from .events.end_event import EndEvent as EndEventMixin
from .events.intermediate_event import (
    IntermediateCatchEvent as IntermediateCatchEventMixin,
    IntermediateThrowEvent as IntermediateThrowEventMixin,
    BoundaryEvent as BoundaryEventMixin,
    EventBasedGateway as EventBasedGatewayMixin,
    SendTask as SendTaskMixin,
    ReceiveTask as ReceiveTaskMixin,
)