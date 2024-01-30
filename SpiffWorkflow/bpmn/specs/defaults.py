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

from .mixins import (
    BpmnSpecMixin,
    ManualTaskMixin,
    NoneTaskMixin,
    UserTaskMixin,
    ExclusiveGatewayMixin,
    InclusiveGatewayMixin,
    ParallelGatewayMixin,
    ScriptTaskMixin,
    ServiceTaskMixin,
    StandardLoopTaskMixin,
    ParallelMultiInstanceTaskMixin,
    SequentialMultiInstanceTaskMixin,
    SubWorkflowTaskMixin,
    CallActivityMixin,
    TransactionSubprocessMixin,
    StartEventMixin,
    EndEventMixin,
    IntermediateCatchEventMixin,
    IntermediateThrowEventMixin,
    SendTaskMixin,
    ReceiveTaskMixin,
    EventBasedGatewayMixin,
    BoundaryEventMixin,
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

class SubWorkflowTask(SubWorkflowTaskMixin, BpmnSpecMixin):
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
