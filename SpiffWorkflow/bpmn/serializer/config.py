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

from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn import BpmnWorkflow, BpmnEvent
from SpiffWorkflow.bpmn.util.subworkflow import BpmnSubWorkflow

from SpiffWorkflow.bpmn.specs import BpmnProcessSpec
from SpiffWorkflow.bpmn.specs.defaults import (
    ManualTask,
    NoneTask,
    UserTask,
    ExclusiveGateway,
    InclusiveGateway,
    ParallelGateway,
    EventBasedGateway,
    ScriptTask,
    ServiceTask,
    StandardLoopTask,
    ParallelMultiInstanceTask,
    SequentialMultiInstanceTask,
    SubWorkflowTask,
    CallActivity,
    TransactionSubprocess,
    StartEvent,
    EndEvent,
    IntermediateCatchEvent,
    IntermediateThrowEvent,
    BoundaryEvent,
    SendTask,
    ReceiveTask,
)
from SpiffWorkflow.bpmn.specs.event_definitions import (
    NoneEventDefinition,
    CancelEventDefinition,
    TerminateEventDefinition,
    SignalEventDefinition,
    ErrorEventDefinition,
    EscalationEventDefinition,
    TimeDateEventDefinition,
    DurationTimerEventDefinition,
    CycleTimerEventDefinition,
    MessageEventDefinition,
    MultipleEventDefinition,
    ConditionalEventDefinition,
)

from SpiffWorkflow.bpmn.specs.control import (
    BpmnStartTask,
    SimpleBpmnTask,
    BoundaryEventSplit,
    BoundaryEventJoin,
    StartEventSplit,
    StartEventJoin,
    _EndJoin,
)
from SpiffWorkflow.bpmn.specs.data_spec import (
    DataObject,
    TaskDataReference,
)
from SpiffWorkflow.bpmn.specs.bpmn_task_spec import BpmnIoSpecification

from .default.workflow import (
    BpmnWorkflowConverter,
    BpmnSubWorkflowConverter,
    TaskConverter,
    BpmnEventConverter,
)
from .helpers import BpmnDataSpecificationConverter, EventDefinitionConverter
from .default import BpmnProcessSpecConverter
from .default.task_spec import (
    BpmnTaskSpecConverter,
    ScriptTaskConverter,
    StandardLoopTaskConverter,
    MultiInstanceTaskConverter,
    SubWorkflowConverter,
    EventJoinConverter,
    ConditionalGatewayConverter,
    ExclusiveGatewayConverter,
    ParallelGatewayConverter,
    EventConverter,
    BoundaryEventConverter,
    IOSpecificationConverter,
)
from .default.event_definition import (
    TimerConditionalEventDefinitionConverter,
    ErrorEscalationEventDefinitionConverter,
    MessageEventDefinitionConverter,
    MultipleEventDefinitionConverter,
)


DEFAULT_CONFIG = {
    BpmnWorkflow: BpmnWorkflowConverter,
    BpmnSubWorkflow: BpmnSubWorkflowConverter,
    Task: TaskConverter,
    BpmnEvent: BpmnEventConverter,
    DataObject: BpmnDataSpecificationConverter,
    TaskDataReference: BpmnDataSpecificationConverter,
    BpmnIoSpecification: IOSpecificationConverter,
    BpmnProcessSpec: BpmnProcessSpecConverter,
    SimpleBpmnTask: BpmnTaskSpecConverter,
    BpmnStartTask: BpmnTaskSpecConverter,
    _EndJoin: BpmnTaskSpecConverter,
    NoneTask: BpmnTaskSpecConverter,
    ManualTask: BpmnTaskSpecConverter,
    UserTask: BpmnTaskSpecConverter,
    ScriptTask: ScriptTaskConverter,
    StandardLoopTask: StandardLoopTaskConverter,
    ParallelMultiInstanceTask: MultiInstanceTaskConverter,
    SequentialMultiInstanceTask: MultiInstanceTaskConverter,
    SubWorkflowTask: SubWorkflowConverter,
    CallActivity: SubWorkflowConverter,
    TransactionSubprocess: SubWorkflowConverter,
    BoundaryEventSplit: BpmnTaskSpecConverter,
    BoundaryEventJoin: EventJoinConverter,
    ExclusiveGateway: ExclusiveGatewayConverter,
    InclusiveGateway: ConditionalGatewayConverter,
    ParallelGateway: ParallelGatewayConverter,
    StartEvent: EventConverter,
    EndEvent: EventConverter,
    IntermediateCatchEvent: EventConverter,
    IntermediateThrowEvent: EventConverter,
    BoundaryEvent: BoundaryEventConverter,
    SendTask: EventConverter,
    ReceiveTask: EventConverter,
    EventBasedGateway: EventConverter,
    CancelEventDefinition: EventDefinitionConverter,
    ErrorEventDefinition: ErrorEscalationEventDefinitionConverter,
    EscalationEventDefinition: ErrorEscalationEventDefinitionConverter,
    MessageEventDefinition: MessageEventDefinitionConverter,
    NoneEventDefinition: EventDefinitionConverter,
    SignalEventDefinition: EventDefinitionConverter,
    TerminateEventDefinition: EventDefinitionConverter,
    TimeDateEventDefinition: TimerConditionalEventDefinitionConverter,
    DurationTimerEventDefinition: TimerConditionalEventDefinitionConverter,
    CycleTimerEventDefinition: TimerConditionalEventDefinitionConverter,
    ConditionalEventDefinition: TimerConditionalEventDefinitionConverter,
    MultipleEventDefinition: MultipleEventDefinitionConverter,
    StartEventSplit: BpmnTaskSpecConverter,
    StartEventJoin: EventJoinConverter,
}
