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
    UserTask as DefaultUserTask,
    ParallelMultiInstanceTask as DefaultParallelMITask,
    SequentialMultiInstanceTask as DefaultSequentialMITask,
    MessageEventDefinition as DefaultMessageEventDefinition,
)

from SpiffWorkflow.camunda.specs.user_task import UserTask
from SpiffWorkflow.camunda.specs.multiinstance_task import ParallelMultiInstanceTask, SequentialMultiInstanceTask
from SpiffWorkflow.camunda.specs.business_rule_task import BusinessRuleTask
from SpiffWorkflow.camunda.specs.event_definitions import MessageEventDefinition

from SpiffWorkflow.bpmn.serializer.default.task_spec import MultiInstanceTaskConverter
from SpiffWorkflow.dmn.serializer.task_spec import BaseBusinessRuleTaskConverter

from .task_spec import UserTaskConverter
from .event_definition import MessageEventDefinitionConverter


CAMUNDA_CONFIG = deepcopy(DEFAULT_CONFIG)

CAMUNDA_CONFIG.pop(DefaultUserTask)
CAMUNDA_CONFIG.pop(DefaultParallelMITask)
CAMUNDA_CONFIG.pop(DefaultSequentialMITask)
CAMUNDA_CONFIG.pop(DefaultMessageEventDefinition)

CAMUNDA_CONFIG[UserTask] = UserTaskConverter
CAMUNDA_CONFIG[ParallelMultiInstanceTask] = MultiInstanceTaskConverter
CAMUNDA_CONFIG[SequentialMultiInstanceTask] = MultiInstanceTaskConverter
CAMUNDA_CONFIG[BusinessRuleTask] = BaseBusinessRuleTaskConverter
CAMUNDA_CONFIG[MessageEventDefinition] = MessageEventDefinitionConverter
