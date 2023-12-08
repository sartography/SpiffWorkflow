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

from SpiffWorkflow.bpmn.serializer.config import DEFAULT_CONFIG
from SpiffWorkflow.bpmn.serializer.config import (
    NoneTask as DefaultNoneTask,
    ManualTask as DefaultManualTask,
    UserTask as DefaultUserTask,
    SendTask as DefaultSendTask,
    ReceiveTask as DefaultReceiveTask,
    ScriptTask as DefaultScriptTask,
    SubWorkflowTask as DefaultSubWorkflowTask,
    TransactionSubprocess as DefaultTransactionSubprocess,
    CallActivity as DefaultCallActivity,
    StandardLoopTask as DefaultStandardLoopTask,
    ParallelMultiInstanceTask as DefaultParallelMultiInstanceTask,
    SequentialMultiInstanceTask as DefaultSequentialMultiInstanceTask,
    MessageEventDefinition as DefaultMessageEventDefinition,
    SignalEventDefinition as DefaultSignalEventDefinition,
    ErrorEventDefinition as DefaultErrorEventDefinition,
    EscalationEventDefinition as DefaultEscalationEventDefinition,
)

from SpiffWorkflow.spiff.specs.defaults import (
    BusinessRuleTask,
    NoneTask,
    ManualTask,
    UserTask,
    SendTask,
    ReceiveTask,
    ScriptTask,
    ServiceTask,
    SubWorkflowTask,
    TransactionSubprocess,
    CallActivity,
    StandardLoopTask,
    ParallelMultiInstanceTask,
    SequentialMultiInstanceTask,
)
from SpiffWorkflow.spiff.specs.event_definitions import (
    MessageEventDefinition,
    SignalEventDefinition,
    ErrorEventDefinition,
    EscalationEventDefinition,
)

from .task_spec import (
    SpiffBpmnTaskConverter,
    SendReceiveTaskConverter,
    ScriptTaskConverter,
    ServiceTaskConverter,
    SubWorkflowTaskConverter,
    StandardLoopTaskConverter,
    SpiffMultiInstanceConverter,
    BusinessRuleTaskConverter,
)
from .event_definition import (
    MessageEventDefinitionConverter,
    ItemAwareEventDefinitionConverter,
    ErrorEscalationEventDefinitionConverter,
)
from SpiffWorkflow.bpmn.specs.data_spec import DataObject as DefaultDataObject
from SpiffWorkflow.spiff.specs.data_object import DataObject
from SpiffWorkflow.spiff.serializer.data_spec import DataObjectConverter

SPIFF_CONFIG = deepcopy(DEFAULT_CONFIG)

SPIFF_CONFIG.pop(DefaultNoneTask)
SPIFF_CONFIG.pop(DefaultManualTask)
SPIFF_CONFIG.pop(DefaultUserTask)
SPIFF_CONFIG.pop(DefaultScriptTask)
SPIFF_CONFIG.pop(DefaultSendTask)
SPIFF_CONFIG.pop(DefaultReceiveTask)
SPIFF_CONFIG.pop(DefaultSubWorkflowTask)
SPIFF_CONFIG.pop(DefaultTransactionSubprocess)
SPIFF_CONFIG.pop(DefaultCallActivity)
SPIFF_CONFIG.pop(DefaultStandardLoopTask)
SPIFF_CONFIG.pop(DefaultParallelMultiInstanceTask)
SPIFF_CONFIG.pop(DefaultSequentialMultiInstanceTask)
SPIFF_CONFIG.pop(DefaultDataObject)

SPIFF_CONFIG[NoneTask] = SpiffBpmnTaskConverter
SPIFF_CONFIG[ManualTask] = SpiffBpmnTaskConverter
SPIFF_CONFIG[UserTask] = SpiffBpmnTaskConverter
SPIFF_CONFIG[ScriptTask] = ScriptTaskConverter
SPIFF_CONFIG[ServiceTask] = ServiceTaskConverter
SPIFF_CONFIG[SendTask] = SendReceiveTaskConverter
SPIFF_CONFIG[ReceiveTask] = SendReceiveTaskConverter
SPIFF_CONFIG[SubWorkflowTask] = SubWorkflowTaskConverter
SPIFF_CONFIG[CallActivity] = SubWorkflowTaskConverter
SPIFF_CONFIG[TransactionSubprocess] = SubWorkflowTaskConverter
SPIFF_CONFIG[ParallelMultiInstanceTask] = SpiffMultiInstanceConverter
SPIFF_CONFIG[SequentialMultiInstanceTask] = SpiffMultiInstanceConverter
SPIFF_CONFIG[MessageEventDefinition] = MessageEventDefinitionConverter
SPIFF_CONFIG[SignalEventDefinition] = ItemAwareEventDefinitionConverter
SPIFF_CONFIG[ErrorEventDefinition] = ErrorEscalationEventDefinitionConverter
SPIFF_CONFIG[EscalationEventDefinition] = ErrorEscalationEventDefinitionConverter
SPIFF_CONFIG[BusinessRuleTask] = BusinessRuleTaskConverter
SPIFF_CONFIG[DataObject] = DataObjectConverter
