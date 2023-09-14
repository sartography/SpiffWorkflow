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

from SpiffWorkflow.bpmn.serializer.default.process_spec import BpmnProcessSpecConverter
from SpiffWorkflow.bpmn.serializer.default.task_spec import (
    SimpleBpmnTaskConverter,
    BpmnStartTaskConverter,
    EndJoinConverter,
    StartEventConverter,
    EndEventConverter, 
    IntermediateCatchEventConverter,
    IntermediateThrowEventConverter,
    EventBasedGatewayConverter,
    BoundaryEventConverter,
    BoundaryEventSplitConverter,
    BoundaryEventJoinConverter,
    ParallelGatewayConverter,
    ExclusiveGatewayConverter,
    InclusiveGatewayConverter,
)

from .task_spec import (
    NoneTaskConverter,
    ManualTaskConverter,
    UserTaskConverter,
    SendTaskConverter,
    ReceiveTaskConverter,
    ScriptTaskConverter,
    ServiceTaskConverter,
    SubprocessTaskConverter,
    TransactionSubprocessConverter,
    CallActivityTaskConverter,
    StandardLoopTaskConverter,
    ParallelMultiInstanceTaskConverter,
    SequentialMultiInstanceTaskConverter,
    BusinessRuleTaskConverter,
)

from SpiffWorkflow.bpmn.serializer.default.event_definition import (
    CancelEventDefinitionConverter,
    NoneEventDefinitionConverter,
    TerminateEventDefinitionConverter,
    TimeDateEventDefinitionConverter,
    DurationTimerEventDefinitionConverter,
    CycleTimerEventDefinitionConverter,
    MultipleEventDefinitionConverter,
)

from .event_definition import (
    MessageEventDefinitionConverter,
    SignalEventDefinitionConverter,
    ErrorEventDefinitionConverter,
    EscalationEventDefinitionConverter,
)

from SpiffWorkflow.bpmn.serializer.default.data_spec import (
    BpmnDataObjectConverter,
    TaskDataReferenceConverter,
    IOSpecificationConverter,
)

from SpiffWorkflow.bpmn.serializer.default.workflow import (
    BpmnWorkflowConverter,
    BpmnSubWorkflowConverter,
    TaskConverter,
    BpmnEventConverter,
)

SPIFF_CONFIG = [
    SimpleBpmnTaskConverter,
    BpmnStartTaskConverter,
    EndJoinConverter,
    StartEventConverter,
    EndEventConverter, 
    IntermediateCatchEventConverter,
    IntermediateThrowEventConverter,
    EventBasedGatewayConverter,
    BoundaryEventConverter,
    BoundaryEventSplitConverter,
    BoundaryEventJoinConverter,
    ParallelGatewayConverter,
    ExclusiveGatewayConverter,
    InclusiveGatewayConverter,
    NoneTaskConverter,
    ManualTaskConverter,
    UserTaskConverter,
    SendTaskConverter,
    ReceiveTaskConverter,
    ScriptTaskConverter,
    ServiceTaskConverter,
    SubprocessTaskConverter,
    TransactionSubprocessConverter,
    CallActivityTaskConverter,
    StandardLoopTaskConverter,
    ParallelMultiInstanceTaskConverter,
    SequentialMultiInstanceTaskConverter,
    BusinessRuleTaskConverter,
    CancelEventDefinitionConverter,
    NoneEventDefinitionConverter,
    TerminateEventDefinitionConverter,
    TimeDateEventDefinitionConverter,
    DurationTimerEventDefinitionConverter,
    CycleTimerEventDefinitionConverter,
    MultipleEventDefinitionConverter,
    MessageEventDefinitionConverter,
    SignalEventDefinitionConverter,
    ErrorEventDefinitionConverter,
    EscalationEventDefinitionConverter,
    BpmnDataObjectConverter,
    TaskDataReferenceConverter,
    IOSpecificationConverter,
    BpmnWorkflowConverter,
    BpmnSubWorkflowConverter,
    TaskConverter,
    BpmnEventConverter,
    BpmnProcessSpecConverter,
]
