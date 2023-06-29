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

from copy import deepcopy

from SpiffWorkflow.bpmn.serializer.workflow import DEFAULT_SPEC_CONFIG
from SpiffWorkflow.bpmn.serializer.task_spec import (
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

from SpiffWorkflow.bpmn.serializer.event_definition import (
    MessageEventDefinitionConverter as DefaultMessageEventDefinitionConverter,
    SignalEventDefinitionConverter as DefaultSignalEventDefinitionConverter,
    ErrorEventDefinitionConverter as DefaultErrorEventDefinitionConverter,
    EscalationEventDefinitionConverter as DefaultEscalationEventDefinitionConverter,
)

from .event_definition import (
    MessageEventDefinitionConverter,
    SignalEventDefinitionConverter,
    ErrorEventDefinitionConverter,
    EscalationEventDefinitionConverter,
)

SPIFF_SPEC_CONFIG = deepcopy(DEFAULT_SPEC_CONFIG)
SPIFF_SPEC_CONFIG['task_specs'] = [
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
    BusinessRuleTaskConverter
]
SPIFF_SPEC_CONFIG['event_definitions'].remove(DefaultMessageEventDefinitionConverter)
SPIFF_SPEC_CONFIG['event_definitions'].remove(DefaultSignalEventDefinitionConverter)
SPIFF_SPEC_CONFIG['event_definitions'].remove(DefaultErrorEventDefinitionConverter)
SPIFF_SPEC_CONFIG['event_definitions'].remove(DefaultEscalationEventDefinitionConverter)
SPIFF_SPEC_CONFIG['event_definitions'].append(MessageEventDefinitionConverter)
SPIFF_SPEC_CONFIG['event_definitions'].append(SignalEventDefinitionConverter)
SPIFF_SPEC_CONFIG['event_definitions'].append(ErrorEventDefinitionConverter)
SPIFF_SPEC_CONFIG['event_definitions'].append(EscalationEventDefinitionConverter)
