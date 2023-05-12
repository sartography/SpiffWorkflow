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

from .mixins.bpmn_spec_mixin import BpmnSpecMixin

from .mixins.manual_task import ManualTask as ManualTaskMixin
from .mixins.none_task import NoneTask as NoneTaskMixin
from .mixins.user_task import UserTask as UserTaskMixin

from .mixins.exclusive_gateway import ExclusiveGateway as ExclusiveGatewayMixin
from .mixins.inclusive_gateway import InclusiveGateway as InclusiveGatewayMixin
from .mixins.parallel_gateway import ParallelGateway as ParallelGatewayMixin

from .mixins.script_task import ScriptTask as ScriptTaskMixin
from .mixins.service_task import ServiceTask as ServiceTaskMixin
from .mixins.multiinstance_task import (
    StandardLoopTask as StandardLoopTaskMixin,
    ParallelMultiInstanceTask as ParallelMultiInstanceTaskMixin,
    SequentialMultiInstanceTask as SequentialMultiInstanceTaskMixin,
)

from .mixins.subworkflow_task import (
    SubWorkflowTask as SubworkflowTaskMixin,
    CallActivity as CallActivityMixin,
    TransactionSubprocess as TransactionSubprocessMixin,
)

from .mixins.events.start_event import StartEvent as StartEventMixin
from .mixins.events.end_event import EndEvent as EndEventMixin
from .mixins.events.intermediate_event import (
    IntermediateCatchEvent as IntermediateCatchEventMixin,
    IntermediateThrowEvent as IntermediateThrowEventMixin,
    SendTask as SendTaskMixin,
    ReceiveTask as ReceiveTaskMixin,
    EventBasedGateway as EventBasedGatewayMixin,
    BoundaryEvent as BoundaryEventMixin,
)

# In the future, we could have the parser take a bpmn task spec and construct these classes automatically
# However, I am NOT going to try to do that with the parser we have now

class ManualTask(ManualTaskMixin, BpmnSpecMixin):
    pass

class NoneTask(NoneTaskMixin, BpmnSpecMixin):
    pass

class UserTask(UserTaskMixin, BpmnSpecMixin):
    pass

class ExclusiveGateway(ExclusiveGatewayMixin, BpmnSpecMixin):
    pass

class InclusiveGateway(InclusiveGatewayMixin, BpmnSpecMixin):
    pass

class ParallelGateway(ParallelGatewayMixin, BpmnSpecMixin):
    pass

class ScriptTask(ScriptTaskMixin, BpmnSpecMixin):
    pass

class ServiceTask(ServiceTaskMixin, BpmnSpecMixin):
    pass

class StandardLoopTask(StandardLoopTaskMixin, BpmnSpecMixin):
    pass

class ParallelMultiInstanceTask(ParallelMultiInstanceTaskMixin, BpmnSpecMixin):
    pass

class SequentialMultiInstanceTask(SequentialMultiInstanceTaskMixin, BpmnSpecMixin):
    pass

class SubWorkflowTask(SubworkflowTaskMixin, BpmnSpecMixin):
    pass

class CallActivity(CallActivityMixin, BpmnSpecMixin):
    pass

class TransactionSubprocess(TransactionSubprocessMixin, BpmnSpecMixin):
    pass

class StartEvent(StartEventMixin, BpmnSpecMixin):
    pass

class EndEvent(EndEventMixin, BpmnSpecMixin):
    pass

class IntermediateCatchEvent(IntermediateCatchEventMixin, BpmnSpecMixin):
    pass

class IntermediateThrowEvent(IntermediateThrowEventMixin, BpmnSpecMixin):
    pass

class SendTask(SendTaskMixin, BpmnSpecMixin):
    pass

class ReceiveTask(ReceiveTaskMixin, BpmnSpecMixin):
    pass

class EventBasedGateway(EventBasedGatewayMixin, BpmnSpecMixin):
    pass

class BoundaryEvent(BoundaryEventMixin, BpmnSpecMixin):
    pass
